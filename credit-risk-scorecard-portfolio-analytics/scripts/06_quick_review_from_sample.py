from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


PROJECT = Path(__file__).resolve().parents[1]
SAMPLE_PATH = PROJECT / "data" / "processed" / "formula_engine_account_sample.csv.gz"
REPORT_DIR = PROJECT / "reports"


REQUIRED_COLUMNS = [
    "loan_id",
    "application_month",
    "matured_flag",
    "bad_flag",
    "fico_band",
    "dti_extreme_or_missing_bin",
    "income_missing_or_invalid_bin",
    "purpose",
    "home_ownership",
    "ead_proxy",
    "lgd_assumption",
    "risk_decile",
    "pd_formula",
    "scorecard_points",
    "risk_grade",
    "policy_action",
    "expected_loss_formula",
]


def pct(value: float) -> str:
    return f"{value:.2%}"


def to_markdown_table(frame: pd.DataFrame) -> str:
    safe = frame.copy()
    for col in safe.columns:
        if pd.api.types.is_float_dtype(safe[col]):
            safe[col] = safe[col].map(lambda value: f"{value:.6f}")
        else:
            safe[col] = safe[col].astype(str)
    headers = list(safe.columns)
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for _, row in safe.iterrows():
        lines.append("| " + " | ".join(str(row[col]).replace("|", "/") for col in headers) + " |")
    return "\n".join(lines)


def main() -> None:
    if not SAMPLE_PATH.exists():
        raise FileNotFoundError(f"Missing sample file: {SAMPLE_PATH}")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    sample = pd.read_csv(SAMPLE_PATH)
    missing = [col for col in REQUIRED_COLUMNS if col not in sample.columns]
    if missing:
        raise AssertionError(f"Sample missing required columns: {missing}")

    rows = len(sample)
    matured_rows = int(sample["matured_flag"].sum())
    default_rate = float(sample["bad_flag"].mean())
    total_ead = float(sample["ead_proxy"].sum())
    total_el = float(sample["expected_loss_formula"].sum())
    avg_pd = float(sample["pd_formula"].mean())

    by_grade = (
        sample.groupby(["risk_grade", "policy_action"], dropna=False)
        .agg(
            accounts=("loan_id", "count"),
            observed_default_rate=("bad_flag", "mean"),
            avg_pd=("pd_formula", "mean"),
            ead_proxy=("ead_proxy", "sum"),
            expected_loss=("expected_loss_formula", "sum"),
        )
        .reset_index()
        .sort_values(["observed_default_rate", "risk_grade"], ascending=[True, True])
    )
    by_grade["el_rate"] = by_grade["expected_loss"] / by_grade["ead_proxy"]
    by_grade.to_csv(REPORT_DIR / "34_sample_quick_review_by_grade.csv", index=False)

    by_decile = (
        sample.groupby("risk_decile", dropna=False)
        .agg(
            accounts=("loan_id", "count"),
            observed_default_rate=("bad_flag", "mean"),
            avg_pd=("pd_formula", "mean"),
            avg_score=("scorecard_points", "mean"),
            ead_proxy=("ead_proxy", "sum"),
            expected_loss=("expected_loss_formula", "sum"),
        )
        .reset_index()
        .sort_values("risk_decile")
    )
    by_decile.to_csv(REPORT_DIR / "34_sample_quick_review_by_decile.csv", index=False)

    summary = {
        "mode": "light_sample_review",
        "sample_path": SAMPLE_PATH.relative_to(PROJECT).as_posix(),
        "sample_rows": rows,
        "matured_rows": matured_rows,
        "observed_default_rate": default_rate,
        "average_formula_pd": avg_pd,
        "ead_proxy": total_ead,
        "expected_loss": total_el,
        "sample_purpose": "Quick reviewer sanity check from included 100k sample; not a full raw-data rebuild.",
        "full_rebuild_note": "Full regeneration requires Project 0 data core as documented in DATA_ACCESS.md.",
    }
    (REPORT_DIR / "34_sample_quick_review_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    markdown = [
        "# Sample Quick Review",
        "",
        "Mode: **light sample review**",
        "",
        "This report is generated from `data/processed/formula_engine_account_sample.csv.gz`. It allows a reviewer to run a lightweight check without recreating Project 0. It does **not** regenerate the full formula engine, WOE/IV tables, validation windows, stress testing or Power BI pack.",
        "",
        "## Headline Sample Checks",
        "",
        f"- Sample rows: **{rows:,}**",
        f"- Matured rows in sample: **{matured_rows:,}**",
        f"- Observed default rate: **{pct(default_rate)}**",
        f"- Average formula PD: **{pct(avg_pd)}**",
        f"- EAD proxy: **{total_ead:,.0f}**",
        f"- Expected loss: **{total_el:,.0f}**",
        "",
        "## Reviewer Quick Run",
        "",
        "```bash",
        "python scripts/06_quick_review_from_sample.py",
        "python scripts/02_validate_project3_outputs.py",
        "```",
        "",
        "## Full Rebuild",
        "",
        "Full rebuild requires the Project 0 data core and public raw datasets documented in `DATA_ACCESS.md`.",
        "",
        "## Risk Grade Summary",
        "",
        to_markdown_table(by_grade),
    ]
    (REPORT_DIR / "34_sample_quick_review.md").write_text("\n".join(markdown), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
