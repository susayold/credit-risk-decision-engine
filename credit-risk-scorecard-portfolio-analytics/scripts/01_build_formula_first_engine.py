from __future__ import annotations

import json
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, roc_curve


PROJECT = Path(__file__).resolve().parents[1]
if "FINANCIAL_RISK_DATA_CORE" not in os.environ:
    raise RuntimeError("Set FINANCIAL_RISK_DATA_CORE to run the full Project 3 rebuild.")
DATA_CORE = Path(os.environ["FINANCIAL_RISK_DATA_CORE"])
PROJECT3_GOLD = DATA_CORE / "data" / "gold" / "project3"

SOURCE_BASE = PROJECT3_GOLD / "project3_credit_risk_account_base.csv.gz"
SOURCE_WOE = PROJECT3_GOLD / "project3_woe_iv_ready_table.csv"
SOURCE_REJECT_PROFILE = PROJECT3_GOLD / "project3_lendingclub_reject_population_profile.csv"
SOURCE_REJECT_SEGMENT = PROJECT3_GOLD / "project3_lendingclub_reject_summary_by_segment.csv"
SOURCE_SBA_PROFILE = PROJECT3_GOLD / "project3_sba_chargeoff_reference_profile.csv"
SOURCE_DATA_GAPS = PROJECT3_GOLD / "project3_data_gap_register.csv"
SOURCE_COVERAGE = PROJECT3_GOLD / "project3_module_data_coverage.csv"

PROCESSED = PROJECT / "data" / "processed"
REPORTS = PROJECT / "reports"
VISUALS = PROJECT / "visuals"
DOCS = PROJECT / "docs"

WOE_VARIABLES = [
    "fico_band",
    "dti_extreme_or_missing_bin",
    "income_missing_or_invalid_bin",
    "purpose",
    "home_ownership",
    "high_dti_flag",
    "high_amount_flag",
]

BASE_SCORE = 600
BASE_GOOD_ODDS = 20
PDO = 50

COLORS = {
    "ink": "#14213d",
    "blue": "#1d5f8a",
    "teal": "#14746f",
    "red": "#a63d40",
    "gold": "#b88732",
    "gray": "#697586",
    "line": "#d9e2ec",
    "bg": "#f7f9fb",
}


def ensure_dirs() -> None:
    for folder in [PROCESSED, REPORTS, VISUALS, DOCS]:
        folder.mkdir(parents=True, exist_ok=True)


def normalize_key(series: pd.Series) -> pd.Series:
    return series.astype("string").fillna("Missing").str.strip()


def ks_stat(y_true: pd.Series, scores: pd.Series) -> float:
    fpr, tpr, _ = roc_curve(y_true, scores)
    return float(np.max(tpr - fpr))


def psi(expected: pd.Series, actual: pd.Series) -> float:
    categories = sorted(set(expected.index).union(set(actual.index)))
    expected = expected.reindex(categories).fillna(0.0001)
    actual = actual.reindex(categories).fillna(0.0001)
    return float(((actual - expected) * np.log(actual / expected)).sum())


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    usecols = [
        "loan_id",
        "application_month",
        "maturity_cutoff_month",
        "matured_flag",
        "monitor_only_flag",
        "default_flag",
        "good_flag",
        "bad_flag",
        "target_population",
        "annual_income",
        "dti",
        "loan_amount",
        "fico_score",
        "fico_band",
        "dti_extreme_or_missing_bin",
        "income_missing_or_invalid_bin",
        "purpose",
        "home_ownership",
        "state",
        "high_dti_flag",
        "high_amount_flag",
        "ead_proxy",
        "lgd_assumption",
        "expected_loss_proxy",
    ]
    base = pd.read_csv(SOURCE_BASE, compression="gzip", usecols=usecols, parse_dates=["application_month"])
    woe = pd.read_csv(SOURCE_WOE)
    return base, woe


def build_woe_maps(woe: pd.DataFrame) -> tuple[dict[str, dict[str, float]], dict[str, float], pd.DataFrame]:
    woe = woe.copy()
    woe["bin_key"] = normalize_key(woe["bin"])
    variable_iv = (
        woe.groupby("variable", as_index=False)["iv_variable_smoothed"]
        .max()
        .rename(columns={"iv_variable_smoothed": "iv"})
        .sort_values("iv", ascending=False)
    )
    variable_iv["iv_weight"] = variable_iv["iv"] / variable_iv["iv"].sum()
    maps: dict[str, dict[str, float]] = {}
    weights: dict[str, float] = {}
    for row in variable_iv.itertuples(index=False):
        variable_rows = woe[woe["variable"] == row.variable]
        maps[row.variable] = dict(zip(variable_rows["bin_key"], variable_rows["woe_smoothed"]))
        weights[row.variable] = float(row.iv_weight)
    return maps, weights, variable_iv


def add_formula_score(base: pd.DataFrame, woe_maps: dict[str, dict[str, float]], weights: dict[str, float]) -> pd.DataFrame:
    out = base.copy()
    out["good_woe_score"] = 0.0
    for variable in WOE_VARIABLES:
        key = normalize_key(out[variable])
        woe_value = key.map(woe_maps.get(variable, {})).astype(float).fillna(0.0)
        out[f"woe_{variable}"] = woe_value
        out["good_woe_score"] += weights.get(variable, 0.0) * woe_value

    out["risk_score_raw"] = -out["good_woe_score"]
    ranks = out["risk_score_raw"].rank(method="first")
    out["risk_decile"] = pd.qcut(ranks, 10, labels=False) + 1
    out["risk_decile"] = out["risk_decile"].astype(int)
    return out


def add_pd_scorecard(out: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    matured = out[out["matured_flag"] == 1].copy()
    decile_pd = (
        matured.groupby("risk_decile")
        .agg(
            accounts=("loan_id", "count"),
            good_accounts=("good_flag", "sum"),
            bad_accounts=("bad_flag", "sum"),
            observed_pd=("bad_flag", "mean"),
            avg_good_woe_score=("good_woe_score", "mean"),
            avg_risk_score_raw=("risk_score_raw", "mean"),
        )
        .reset_index()
    )
    portfolio_pd = float(matured["bad_flag"].mean())
    out = out.merge(decile_pd[["risk_decile", "observed_pd"]], on="risk_decile", how="left")
    out["pd_formula"] = out["observed_pd"].fillna(portfolio_pd).clip(0.0001, 0.9999)
    good_odds = (1 - out["pd_formula"]) / out["pd_formula"]
    factor = PDO / np.log(2)
    offset = BASE_SCORE - factor * np.log(BASE_GOOD_ODDS)
    out["scorecard_points"] = offset + factor * np.log(good_odds)
    out["expected_loss_formula"] = out["pd_formula"] * out["lgd_assumption"] * out["ead_proxy"]
    out["el_rate_formula"] = out["expected_loss_formula"] / out["ead_proxy"].replace(0, np.nan)
    out["risk_grade"] = pd.cut(
        out["pd_formula"],
        bins=[-np.inf, 0.10, 0.15, 0.20, 0.25, np.inf],
        labels=["A - Low", "B - Moderate", "C - Watch", "D - High", "E - Very High"],
    )
    out["policy_action"] = np.select(
        [
            out["pd_formula"] <= 0.10,
            out["pd_formula"] <= 0.15,
            out["pd_formula"] <= 0.20,
            out["pd_formula"] <= 0.25,
            out["pd_formula"] > 0.25,
        ],
        [
            "Auto approve",
            "Approve standard",
            "Approve with limit/pricing control",
            "Manual review",
            "Decline or require mitigants",
        ],
        default="Review",
    )
    return out, decile_pd


def population_summary(base: pd.DataFrame) -> pd.DataFrame:
    rows = [
        ("account_rows", len(base)),
        ("matured_rows", int(base["matured_flag"].sum())),
        ("monitor_only_rows", int(base["monitor_only_flag"].sum())),
        ("matured_default_rate", float(base.loc[base["matured_flag"] == 1, "bad_flag"].mean())),
        ("total_ead_proxy", float(base["ead_proxy"].sum())),
        ("total_expected_loss_formula", float(base["expected_loss_formula"].sum())),
        ("average_pd_formula", float(base["pd_formula"].mean())),
        ("average_lgd_assumption", float(base["lgd_assumption"].mean())),
        ("average_scorecard_points", float(base["scorecard_points"].mean())),
    ]
    return pd.DataFrame(rows, columns=["metric", "value"])


def score_band_summary(base: pd.DataFrame) -> pd.DataFrame:
    matured = base[base["matured_flag"] == 1].copy()
    out = (
        matured.groupby(["risk_grade", "policy_action"], observed=True)
        .agg(
            accounts=("loan_id", "count"),
            good_accounts=("good_flag", "sum"),
            bad_accounts=("bad_flag", "sum"),
            observed_default_rate=("bad_flag", "mean"),
            avg_pd=("pd_formula", "mean"),
            avg_score=("scorecard_points", "mean"),
            ead_proxy=("ead_proxy", "sum"),
            expected_loss=("expected_loss_formula", "sum"),
        )
        .reset_index()
    )
    out["el_rate"] = out["expected_loss"] / out["ead_proxy"].replace(0, np.nan)
    out["account_share"] = out["accounts"] / out["accounts"].sum()
    return out


def validation_metrics(base: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for sample, frame in [
        ("matured_all", base[base["matured_flag"] == 1]),
        ("train_pre_2016", base[(base["matured_flag"] == 1) & (base["application_month"] <= "2015-12-01")]),
        (
            "validation_2016",
            base[(base["matured_flag"] == 1) & (base["application_month"].between("2016-01-01", "2016-12-01"))],
        ),
        (
            "test_2017",
            base[(base["matured_flag"] == 1) & (base["application_month"].between("2017-01-01", "2017-12-01"))],
        ),
    ]:
        if frame.empty:
            continue
        y = frame["bad_flag"]
        scores = frame["pd_formula"]
        auc = roc_auc_score(y, scores)
        brier = float(np.mean((scores - y) ** 2))
        rows.append(
            {
                "sample": sample,
                "rows": len(frame),
                "observed_default_rate": float(y.mean()),
                "average_pd": float(scores.mean()),
                "calibration_gap": float(y.mean() - scores.mean()),
                "auc": float(auc),
                "gini": float(2 * auc - 1),
                "ks": ks_stat(y, scores),
                "brier_score": brier,
            }
        )
    return pd.DataFrame(rows)


def calibration_by_decile(base: pd.DataFrame) -> pd.DataFrame:
    matured = base[base["matured_flag"] == 1].copy()
    out = (
        matured.groupby("risk_decile")
        .agg(
            accounts=("loan_id", "count"),
            observed_default_rate=("bad_flag", "mean"),
            avg_pd=("pd_formula", "mean"),
            avg_score=("scorecard_points", "mean"),
            good_woe_score=("good_woe_score", "mean"),
        )
        .reset_index()
        .sort_values("risk_decile")
    )
    out["calibration_gap"] = out["observed_default_rate"] - out["avg_pd"]
    return out


def cutoff_strategy(base: pd.DataFrame) -> pd.DataFrame:
    matured = base[base["matured_flag"] == 1].copy()
    rows = []
    for cutoff in [0.10, 0.12, 0.15, 0.18, 0.20, 0.22, 0.25, 0.30, 0.35]:
        approved = matured["pd_formula"] <= cutoff
        reviewed_or_declined = ~approved
        rows.append(
            {
                "pd_cutoff": cutoff,
                "approved_accounts": int(approved.sum()),
                "review_or_decline_accounts": int(reviewed_or_declined.sum()),
                "approval_rate": float(approved.mean()),
                "approved_default_rate": float(matured.loc[approved, "bad_flag"].mean()) if approved.any() else np.nan,
                "review_or_decline_default_rate": float(matured.loc[reviewed_or_declined, "bad_flag"].mean()) if reviewed_or_declined.any() else np.nan,
                "bad_capture_in_review_or_decline": float(matured.loc[reviewed_or_declined, "bad_flag"].sum() / matured["bad_flag"].sum()),
                "approved_ead_proxy": float(matured.loc[approved, "ead_proxy"].sum()),
                "approved_expected_loss": float(matured.loc[approved, "expected_loss_formula"].sum()),
                "approved_el_rate": float(
                    matured.loc[approved, "expected_loss_formula"].sum() / matured.loc[approved, "ead_proxy"].sum()
                )
                if approved.any()
                else np.nan,
            }
        )
    return pd.DataFrame(rows)


def expected_loss_summary(base: pd.DataFrame) -> pd.DataFrame:
    out = (
        base.groupby(["risk_grade", "policy_action"], observed=True)
        .agg(
            accounts=("loan_id", "count"),
            ead_proxy=("ead_proxy", "sum"),
            expected_loss=("expected_loss_formula", "sum"),
            avg_pd=("pd_formula", "mean"),
            avg_lgd=("lgd_assumption", "mean"),
            avg_score=("scorecard_points", "mean"),
        )
        .reset_index()
    )
    out["ead_share"] = out["ead_proxy"] / out["ead_proxy"].sum()
    out["expected_loss_share"] = out["expected_loss"] / out["expected_loss"].sum()
    out["el_rate"] = out["expected_loss"] / out["ead_proxy"].replace(0, np.nan)
    return out


def monitoring_psi(base: pd.DataFrame) -> pd.DataFrame:
    frame = base[base["matured_flag"] == 1].copy()
    baseline = frame[frame["application_month"].dt.year == 2015]["risk_grade"].value_counts(normalize=True)
    rows = []
    for year, group in frame.groupby(frame["application_month"].dt.year):
        actual = group["risk_grade"].value_counts(normalize=True)
        rows.append(
            {
                "year": int(year),
                "accounts": len(group),
                "default_rate": float(group["bad_flag"].mean()),
                "avg_pd": float(group["pd_formula"].mean()),
                "psi_vs_2015": psi(baseline, actual) if not baseline.empty else np.nan,
            }
        )
    return pd.DataFrame(rows)


def reject_inference_summary(base: pd.DataFrame) -> pd.DataFrame:
    reject_profile = pd.read_csv(SOURCE_REJECT_PROFILE)
    reject_rows = int(float(reject_profile.loc[reject_profile["metric"] == "reject_cleaned_rows", "value"].iloc[0]))
    approved_bad_rate = float(base.loc[base["matured_flag"] == 1, "bad_flag"].mean())
    rows = []
    for uplift in [1.0, 1.5, 2.0, 3.0]:
        reject_bad_rate = min(approved_bad_rate * uplift, 1.0)
        rows.append(
            {
                "scenario": f"{uplift:.1f}x approved/booked bad rate",
                "approved_bad_rate": approved_bad_rate,
                "assumed_reject_bad_rate": reject_bad_rate,
                "rejected_applications": reject_rows,
                "inferred_reject_bad_count": int(round(reject_rows * reject_bad_rate)),
                "interpretation": "Sensitivity only: reject outcomes are not observed.",
            }
        )
    return pd.DataFrame(rows)


def formula_dictionary() -> pd.DataFrame:
    rows = [
        ("Default Rate", "Bad accounts / matured accounts", "Observed default frequency on matured accounts only."),
        ("WOE", "LN(%Good_bin / %Bad_bin)", "Direction and strength of a bin's good/bad separation."),
        ("IV", "SUM((%Good_bin - %Bad_bin) * WOE_bin)", "Variable-level separation power."),
        ("Good Odds", "(1 - PD) / PD", "Credit scorecard convention used for points."),
        ("Scorecard Points", "Offset + Factor * LN(Good Odds)", "Business-friendly score where higher means lower risk."),
        ("Expected Loss", "PD x LGD x EAD", "Expected credit loss proxy at account, band and portfolio level."),
        ("AUC", "Ranking metric", "Probability that a bad account ranks riskier than a good account."),
        ("Gini", "2 x AUC - 1", "Credit-risk ranking metric derived from AUC."),
        ("KS", "MAX(TPR - FPR)", "Maximum separation between cumulative bad and good distributions."),
        ("Brier Score", "AVG((PD - Default_Flag)^2)", "Probability accuracy metric; lower is better."),
        ("PSI", "SUM((Actual% - Expected%) x LN(Actual% / Expected%))", "Population shift monitoring metric."),
    ]
    return pd.DataFrame(rows, columns=["formula", "definition", "business_meaning"])


def write_markdown_reports(
    population: pd.DataFrame,
    validation: pd.DataFrame,
    score_bands: pd.DataFrame,
    cutoffs: pd.DataFrame,
    reject_summary: pd.DataFrame,
) -> None:
    metrics = dict(zip(population["metric"], population["value"]))
    test = validation[validation["sample"] == "test_2017"].iloc[0]
    recommended = cutoffs.loc[cutoffs["pd_cutoff"].eq(0.20)].iloc[0]
    text = f"""# Executive Summary - Project 3 Formula-First Credit Risk Engine

## Business Question

Which accepted/booked lending accounts are likely to default, how should they be ranked into risk bands, and what approval or review action should follow?

## Data Foundation

- Account rows: {int(metrics['account_rows']):,}
- Matured rows: {int(metrics['matured_rows']):,}
- Monitor-only rows: {int(metrics['monitor_only_rows']):,}
- Matured default rate: {float(metrics['matured_default_rate']):.2%}
- Total EAD-proxy units: {float(metrics['total_ead_proxy']):,.0f}
- Formula expected loss: {float(metrics['total_expected_loss_formula']):,.0f}

## Formula Engine Result

- Test AUC: {test['auc']:.3f}
- Test Gini: {test['gini']:.3f}
- Test KS: {test['ks']:.3f}
- Test Brier score: {test['brier_score']:.3f}
- Test calibration gap: {test['calibration_gap']:.2%}

## Cutoff Strategy

At PD cutoff {recommended['pd_cutoff']:.0%}:

- Approval rate: {recommended['approval_rate']:.2%}
- Approved default rate: {recommended['approved_default_rate']:.2%}
- Review/decline default rate: {recommended['review_or_decline_default_rate']:.2%}
- Bad capture in review/decline group: {recommended['bad_capture_in_review_or_decline']:.2%}
- Approved EL rate: {recommended['approved_el_rate']:.2%}

## Risk Governance Note

This is a formula-first portfolio project. Rejected applicant population is available, but rejected applicant default outcomes are not observed. Therefore reject inference is treated as sensitivity analysis, not as a labeled reject model.
"""
    (REPORTS / "executive_summary.md").write_text(text, encoding="utf-8")

    model_card = f"""# Model Card - Formula-First Credit Risk Engine

## Intended Use

Credit risk education, portfolio analytics, scorecard mechanics, cutoff simulation and recruiter-facing demonstration.

## Not Intended Use

Production underwriting, automated credit approval, regulatory capital reporting or audited IFRS 9 provisioning.

## Data

Core population: accepted/booked consumer lending accounts.

Target: bad account flag on matured accounts.

Observation date: application month.

Performance window assumption: 12 months.

## Method

This version uses WOE/IV-based formula scoring instead of machine learning. Variables are mapped to smoothed WOE bins, combined using IV-based weights, converted into formula PD by score decile, and translated into scorecard points using good-odds convention.

## Key Metrics

| Metric | Test 2017 |
|---|---:|
| AUC | {test['auc']:.3f} |
| Gini | {test['gini']:.3f} |
| KS | {test['ks']:.3f} |
| Brier Score | {test['brier_score']:.3f} |
| Calibration Gap | {test['calibration_gap']:.2%} |

## Metric Interpretation

- AUC {test['auc']:.3f} indicates **moderate ranking power**. It is useful for a transparent formula-first risk baseline, but it is not a strong production underwriting model.
- KS {test['ks']:.3f} confirms moderate good/bad separation.
- Calibration by score decile is mechanically close because formula PD is assigned from observed default rate by risk decile.
- The more realistic calibration assessment is the 2017 out-of-time sample. The test calibration gap is **{test['calibration_gap']:.2%}**, meaning observed default is higher than average predicted PD when positive.
- This model is suitable for portfolio demonstration, risk analytics explanation and policy simulation, not for automated production approval.

## Limitations

- Reject outcomes are unobserved.
- True monthly DPD roll-rate is unavailable in the consumer-loan core.
- Consumer-loan recovery cashflows are unavailable.
- LGD and EAD are proxy assumptions.
- RAROC requires funding, operating and capital cost assumptions.
"""
    (DOCS / "model_card.md").write_text(model_card, encoding="utf-8")


def plot_outputs(score_bands: pd.DataFrame, cutoffs: pd.DataFrame, expected_loss: pd.DataFrame, monitoring: pd.DataFrame) -> None:
    score_plot = score_bands.dropna(subset=["risk_grade"]).copy()
    fig, ax = plt.subplots(figsize=(9, 5.2), facecolor=COLORS["bg"])
    ax.bar(score_plot["risk_grade"].astype(str), score_plot["observed_default_rate"], color=COLORS["blue"])
    ax.set_title("Observed Default Rate by Risk Grade", loc="left", color=COLORS["ink"], fontweight="bold")
    ax.set_ylabel("Observed default rate")
    ax.grid(axis="y", color=COLORS["line"])
    plt.xticks(rotation=20, ha="right")
    fig.tight_layout()
    fig.savefig(VISUALS / "observed_default_by_risk_grade.png", dpi=170, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 5.2), facecolor=COLORS["bg"])
    ax.plot(cutoffs["pd_cutoff"], cutoffs["approval_rate"], marker="o", color=COLORS["teal"], label="Approval rate")
    ax.plot(cutoffs["pd_cutoff"], cutoffs["approved_default_rate"], marker="o", color=COLORS["red"], label="Approved default rate")
    ax.plot(
        cutoffs["pd_cutoff"],
        cutoffs["bad_capture_in_review_or_decline"],
        marker="o",
        color=COLORS["gold"],
        label="Bad capture in review/decline",
    )
    ax.set_title("Cutoff Trade-off", loc="left", color=COLORS["ink"], fontweight="bold")
    ax.set_xlabel("PD cutoff")
    ax.grid(True, color=COLORS["line"])
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(VISUALS / "cutoff_tradeoff.png", dpi=170, bbox_inches="tight")
    plt.close(fig)

    el_plot = expected_loss.dropna(subset=["risk_grade"]).copy()
    fig, ax = plt.subplots(figsize=(9, 5.2), facecolor=COLORS["bg"])
    ax.bar(el_plot["risk_grade"].astype(str), el_plot["expected_loss"], color=COLORS["red"])
    ax.set_title("Expected Loss by Risk Grade", loc="left", color=COLORS["ink"], fontweight="bold")
    ax.set_ylabel("Expected loss proxy")
    ax.grid(axis="y", color=COLORS["line"])
    plt.xticks(rotation=20, ha="right")
    fig.tight_layout()
    fig.savefig(VISUALS / "expected_loss_by_risk_grade.png", dpi=170, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 5.2), facecolor=COLORS["bg"])
    ax.plot(monitoring["year"], monitoring["psi_vs_2015"], marker="o", color=COLORS["blue"])
    ax.axhline(0.10, color=COLORS["gold"], linestyle="--", label="Watchlist 0.10")
    ax.axhline(0.25, color=COLORS["red"], linestyle="--", label="Breach 0.25")
    ax.set_title("Population Stability Index vs 2015", loc="left", color=COLORS["ink"], fontweight="bold")
    ax.set_xlabel("Application year")
    ax.set_ylabel("PSI")
    ax.grid(True, color=COLORS["line"])
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(VISUALS / "psi_monitoring.png", dpi=170, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    ensure_dirs()
    base, woe = load_inputs()
    woe_maps, weights, variable_iv = build_woe_maps(woe)
    scored = add_formula_score(base, woe_maps, weights)
    scored, decile_pd = add_pd_scorecard(scored)

    population = population_summary(scored)
    score_bands = score_band_summary(scored)
    validation = validation_metrics(scored)
    calibration = calibration_by_decile(scored)
    cutoffs = cutoff_strategy(scored)
    expected_loss = expected_loss_summary(scored)
    monitoring = monitoring_psi(scored)
    reject_summary = reject_inference_summary(scored)
    formulas = formula_dictionary()

    scored_sample_cols = [
        "loan_id",
        "application_month",
        "matured_flag",
        "target_population",
        "bad_flag",
        "fico_band",
        "dti_extreme_or_missing_bin",
        "income_missing_or_invalid_bin",
        "purpose",
        "home_ownership",
        "ead_proxy",
        "lgd_assumption",
        "good_woe_score",
        "risk_decile",
        "pd_formula",
        "scorecard_points",
        "risk_grade",
        "policy_action",
        "expected_loss_formula",
    ]
    scored[scored_sample_cols].sample(n=min(100_000, len(scored)), random_state=42).to_csv(
        PROCESSED / "formula_engine_account_sample.csv.gz", index=False, compression="gzip"
    )

    population.to_csv(REPORTS / "01_population_target_summary.csv", index=False)
    formulas.to_csv(REPORTS / "02_formula_dictionary.csv", index=False)
    variable_iv.to_csv(REPORTS / "03_woe_iv_variable_summary.csv", index=False)
    decile_pd.to_csv(REPORTS / "04_decile_pd_mapping.csv", index=False)
    score_bands.to_csv(REPORTS / "05_score_band_summary.csv", index=False)
    validation.to_csv(REPORTS / "06_validation_metrics.csv", index=False)
    calibration.to_csv(REPORTS / "07_calibration_by_decile.csv", index=False)
    cutoffs.to_csv(REPORTS / "08_cutoff_strategy.csv", index=False)
    expected_loss.to_csv(REPORTS / "09_expected_loss_by_risk_grade.csv", index=False)
    monitoring.to_csv(REPORTS / "10_monitoring_psi.csv", index=False)
    reject_summary.to_csv(REPORTS / "11_reject_inference_sensitivity.csv", index=False)
    pd.read_csv(SOURCE_DATA_GAPS).to_csv(REPORTS / "12_data_gap_status.csv", index=False)
    pd.read_csv(SOURCE_COVERAGE).to_csv(REPORTS / "13_module_coverage_status.csv", index=False)
    pd.read_csv(SOURCE_REJECT_SEGMENT).head(5000).to_csv(REPORTS / "14_reject_segment_summary_sample.csv", index=False)
    if SOURCE_SBA_PROFILE.exists():
        pd.read_csv(SOURCE_SBA_PROFILE).to_csv(REPORTS / "15_sba_chargeoff_reference_profile.csv", index=False)

    summary = {
        "project": "Project 3 - Formula-First Credit Risk Modeling",
        "account_rows": int(len(scored)),
        "matured_rows": int(scored["matured_flag"].sum()),
        "matured_default_rate": float(scored.loc[scored["matured_flag"] == 1, "bad_flag"].mean()),
        "test_auc": float(validation.loc[validation["sample"] == "test_2017", "auc"].iloc[0]),
        "test_ks": float(validation.loc[validation["sample"] == "test_2017", "ks"].iloc[0]),
        "test_brier": float(validation.loc[validation["sample"] == "test_2017", "brier_score"].iloc[0]),
        "reject_population_rows": int(reject_summary["rejected_applications"].iloc[0]),
    }
    (REPORTS / "formula_engine_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    write_markdown_reports(population, validation, score_bands, cutoffs, reject_summary)
    plot_outputs(score_bands, cutoffs, expected_loss, monitoring)
    print("Project 3 formula-first engine completed")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
