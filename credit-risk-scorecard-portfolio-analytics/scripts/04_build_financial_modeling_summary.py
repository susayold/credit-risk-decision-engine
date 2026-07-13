from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT = Path(__file__).resolve().parents[1]
REPORTS = PROJECT / "reports"


def pct(value: float) -> str:
    return f"{value:.2%}"


def money(value: float) -> str:
    abs_value = abs(value)
    if abs_value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"
    if abs_value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    if abs_value >= 1_000:
        return f"{value / 1_000:.2f}K"
    return f"{value:.2f}"


def whole(value: float) -> str:
    return f"{value:,.0f}"


def md_table(frame: pd.DataFrame) -> str:
    safe = frame.copy().astype(str)
    headers = list(safe.columns)
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for _, row in safe.iterrows():
        lines.append("| " + " | ".join(str(row[col]).replace("|", "/") for col in headers) + " |")
    return "\n".join(lines)


def load_tables() -> dict[str, pd.DataFrame]:
    return {
        "population": pd.read_csv(REPORTS / "01_population_target_summary.csv"),
        "validation": pd.read_csv(REPORTS / "06_validation_metrics.csv"),
        "score": pd.read_csv(REPORTS / "05_score_band_summary.csv"),
        "el": pd.read_csv(REPORTS / "09_expected_loss_by_risk_grade.csv"),
        "cutoff": pd.read_csv(REPORTS / "08_cutoff_strategy.csv"),
        "stress": pd.read_csv(REPORTS / "22_stress_testing_scenarios.csv"),
        "pricing": pd.read_csv(REPORTS / "23_risk_based_pricing_by_grade.csv"),
        "ecl": pd.read_csv(REPORTS / "21_ifrs9_ecl_bridge.csv"),
        "concentration": pd.read_csv(REPORTS / "25_concentration_risk_by_segment.csv"),
        "vintage": pd.read_csv(REPORTS / "19_vintage_analysis.csv"),
        "override": pd.read_csv(REPORTS / "27_override_policy_simulation.csv"),
        "tests": pd.read_csv(REPORTS / "29_formula_test_cases.csv"),
    }


def build_kpi_summary(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    pop = tables["population"].set_index("metric")["value"]
    validation = tables["validation"]
    test = validation.loc[validation["sample"].eq("test_2017")].iloc[0]
    cutoff_20 = tables["cutoff"].loc[np.isclose(tables["cutoff"]["pd_cutoff"], 0.20)].iloc[0]
    stress = tables["stress"].groupby("scenario", as_index=False).agg(
        stressed_ead=("stressed_ead", "sum"),
        stressed_expected_loss=("stressed_el", "sum"),
    )
    stress["stressed_el_rate"] = stress["stressed_expected_loss"] / stress["stressed_ead"]
    severe = stress.loc[stress["scenario"].eq("Severe")].iloc[0]
    pricing = tables["pricing"]

    rows = [
        ("Portfolio accounts", pop["account_rows"], "Scale", "1.35M accounts is large enough for portfolio-level risk segmentation."),
        ("Matured accounts", pop["matured_rows"], "Target quality", "Matured-only outcomes prevent recent accounts from being incorrectly treated as good."),
        ("Matured default rate", pop["matured_default_rate"], "Credit loss risk", "Base portfolio risk is material at 20.16%; cutoff and pricing control are required."),
        ("Total EAD-proxy units", pop["total_ead_proxy"], "Exposure", "Total exposure proxy is the financial base for EL, stress and pricing."),
        ("Formula expected loss", pop["total_expected_loss_formula"], "Expected loss", "Baseline EL is about 1.53B before final policy action."),
        ("Formula EL rate", pop["total_expected_loss_formula"] / pop["total_ead_proxy"], "Expected loss", "Portfolio EL rate is about 7.88%, so approval policy must avoid blindly maximizing volume."),
        ("Test AUC", test["auc"], "Model ranking", "AUC is acceptable for a transparent formula-first baseline, but not strong enough for automated production approval alone."),
        ("Test KS", test["ks"], "Model separation", "KS confirms moderate separation between good and bad accounts."),
        ("20% cutoff approval rate", cutoff_20["approval_rate"], "Policy", "Approves about half the matured book while keeping higher-risk accounts in review/decline."),
        ("20% cutoff approved default rate", cutoff_20["approved_default_rate"], "Policy", "Approved default rate drops below portfolio average."),
        ("20% cutoff approved EAD", cutoff_20["approved_ead_proxy"], "Exposure approved", "At this cutoff the engine approves about 9.78B EAD."),
        ("20% cutoff approved EL", cutoff_20["approved_expected_loss"], "Loss approved", "Approved EL is about 511M, or 5.23% of approved EAD."),
        ("Bad capture in review/decline", cutoff_20["bad_capture_in_review_or_decline"], "Risk control", "The review/decline group captures 64.07% of bad accounts."),
        ("Severe stressed EL", severe["stressed_expected_loss"], "Stress testing", "Severe scenario EL rises to about 3.82B, showing material downside sensitivity."),
        ("Severe stressed EL rate", severe["stressed_el_rate"], "Stress testing", "Stress EL rate reaches 18.71%, requiring contingency policy."),
        ("Lowest required rate", pricing["required_rate"].min(), "Pricing", "Low-risk grade still needs about 12.55% required rate under assumptions."),
        ("Highest required rate", pricing["required_rate"].max(), "Pricing", "Very-high-risk grade needs about 28.13%, supporting decline/mitigant action."),
        ("Formula tests passed", tables["tests"]["status"].eq("PASS").sum(), "Controls", "Formula logic has test evidence instead of only visual storytelling."),
    ]
    return pd.DataFrame(rows, columns=["metric", "raw_value", "category", "conclusion"])


def build_formatted_tables(tables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    score = tables["score"].copy()
    score_view = pd.DataFrame(
        {
            "Risk grade": score["risk_grade"],
            "Action": score["policy_action"],
            "Accounts": score["accounts"].map(whole),
            "Account share": score["account_share"].map(pct),
            "Default rate": score["observed_default_rate"].map(pct),
            "Avg PD": score["avg_pd"].map(pct),
            "Avg score": score["avg_score"].map(lambda x: f"{x:.0f}"),
            "EAD": score["ead_proxy"].map(money),
            "Expected loss": score["expected_loss"].map(money),
            "EL rate": score["el_rate"].map(pct),
        }
    )

    cutoff = tables["cutoff"].copy()
    cutoff = cutoff[cutoff["pd_cutoff"].isin([0.10, 0.15, 0.20, 0.25, 0.35])]
    cutoff_view = pd.DataFrame(
        {
            "PD cutoff": cutoff["pd_cutoff"].map(pct),
            "Approved accounts": cutoff["approved_accounts"].map(whole),
            "Approval rate": cutoff["approval_rate"].map(pct),
            "Approved default rate": cutoff["approved_default_rate"].map(pct),
            "Review/decline default rate": cutoff["review_or_decline_default_rate"].map(lambda x: "" if pd.isna(x) else pct(x)),
            "Bad capture review/decline": cutoff["bad_capture_in_review_or_decline"].map(pct),
            "Approved EAD": cutoff["approved_ead_proxy"].map(money),
            "Approved EL": cutoff["approved_expected_loss"].map(money),
            "Approved EL rate": cutoff["approved_el_rate"].map(pct),
        }
    )

    stress = tables["stress"].groupby("scenario", as_index=False).agg(
        accounts=("accounts", "sum"),
        stressed_ead=("stressed_ead", "sum"),
        stressed_expected_loss=("stressed_el", "sum"),
    )
    stress["stressed_el_rate"] = stress["stressed_expected_loss"] / stress["stressed_ead"]
    order = {"Base": 1, "Mild Downturn": 2, "Adverse": 3, "Severe": 4}
    stress = stress.sort_values("scenario", key=lambda s: s.map(order))
    stress_view = pd.DataFrame(
        {
            "Scenario": stress["scenario"],
            "Accounts": stress["accounts"].map(whole),
            "Stressed EAD": stress["stressed_ead"].map(money),
            "Stressed EL": stress["stressed_expected_loss"].map(money),
            "Stressed EL rate": stress["stressed_el_rate"].map(pct),
        }
    )

    pricing = tables["pricing"].copy()
    pricing_view = pd.DataFrame(
        {
            "Risk grade": pricing["risk_grade"],
            "EL rate": pricing["el_rate"].map(pct),
            "Funding": pricing["funding_cost_rate"].map(pct),
            "OpEx": pricing["operating_cost_rate"].map(pct),
            "Capital cost": pricing["capital_cost_rate"].map(pct),
            "Profit margin": pricing["profit_margin_rate"].map(pct),
            "Required rate": pricing["required_rate"].map(pct),
            "Offered rate": pricing["illustrative_offered_rate"].map(pct),
            "RAROC proxy": pricing["raroc_proxy"].map(pct),
        }
    )

    ecl = tables["ecl"].groupby("stage", as_index=False).agg(
        accounts=("accounts", "sum"),
        ead=("ead", "sum"),
        ecl_base=("ecl_12m_or_base", "sum"),
        ecl_lifetime=("ecl_lifetime_proxy", "sum"),
    )
    ecl["base_ecl_rate"] = ecl["ecl_base"] / ecl["ead"]
    ecl["lifetime_ecl_rate"] = ecl["ecl_lifetime"] / ecl["ead"]
    ecl_view = pd.DataFrame(
        {
            "Stage": ecl["stage"],
            "Accounts": ecl["accounts"].map(whole),
            "EAD": ecl["ead"].map(money),
            "Base/12m ECL": ecl["ecl_base"].map(money),
            "Lifetime ECL proxy": ecl["ecl_lifetime"].map(money),
            "Base ECL rate": ecl["base_ecl_rate"].map(pct),
            "Lifetime ECL rate": ecl["lifetime_ecl_rate"].map(pct),
        }
    )

    concentration = tables["concentration"].copy()
    concentration = concentration.sort_values("expected_loss", ascending=False).head(12)
    concentration_view = pd.DataFrame(
        {
            "Segment type": concentration["segment_variable"],
            "Segment": concentration["segment_value"],
            "Accounts": concentration["accounts"].map(whole),
            "Default rate": concentration["default_rate_matured"].map(lambda x: "" if pd.isna(x) else pct(x)),
            "EAD": concentration["ead"].map(money),
            "Expected loss": concentration["expected_loss"].map(money),
            "EL share": concentration["el_share"].map(pct),
            "Flag": concentration["concentration_flag"],
        }
    )

    vintage = tables["vintage"].copy()
    vintage = vintage[vintage["matured_accounts"].ge(1000)].sort_values("vintage_bad_rate", ascending=False).head(10)
    vintage_view = pd.DataFrame(
        {
            "Vintage month": vintage["vintage_month"],
            "Accounts": vintage["accounts"].map(whole),
            "Bad accounts": vintage["bad_accounts"].map(whole),
            "Vintage bad rate": vintage["vintage_bad_rate"].map(pct),
            "Avg PD": vintage["avg_pd"].map(pct),
            "Expected loss": vintage["expected_loss"].map(money),
            "EL rate": vintage["el_rate"].map(pct),
        }
    )

    return {
        "score": score_view,
        "cutoff": cutoff_view,
        "stress": stress_view,
        "pricing": pricing_view,
        "ecl": ecl_view,
        "concentration": concentration_view,
        "vintage": vintage_view,
    }


def build_conclusions(tables: dict[str, pd.DataFrame]) -> list[str]:
    cutoff_20 = tables["cutoff"].loc[np.isclose(tables["cutoff"]["pd_cutoff"], 0.20)].iloc[0]
    pricing = tables["pricing"]
    concentration = tables["concentration"]
    debt = concentration[
        concentration["segment_variable"].eq("purpose") & concentration["segment_value"].eq("debt_consolidation")
    ].iloc[0]
    high_risk = tables["score"][tables["score"]["risk_grade"].isin(["D - High", "E - Very High"])]
    high_risk_ead = high_risk["ead_proxy"].sum()
    high_risk_el = high_risk["expected_loss"].sum()
    total_score_ead = tables["score"]["ead_proxy"].sum()
    total_score_el = tables["score"]["expected_loss"].sum()
    severe = tables["stress"].groupby("scenario")["stressed_el"].sum().loc["Severe"]
    base = tables["stress"].groupby("scenario")["stressed_el"].sum().loc["Base"]
    return [
        f"At the 20% PD cutoff, the engine approves {pct(cutoff_20['approval_rate'])} of matured accounts and {money(cutoff_20['approved_ead_proxy'])} EAD, while keeping approved EL rate at {pct(cutoff_20['approved_el_rate'])}.",
        f"The review/decline population captures {pct(cutoff_20['bad_capture_in_review_or_decline'])} of bad accounts, so the cutoff is doing real risk control rather than only reducing volume.",
        f"High-risk grades D and E hold {pct(high_risk_ead / total_score_ead)} of matured EAD but produce {pct(high_risk_el / total_score_el)} of matured expected loss; this supports manual review, mitigants, pricing control or decline.",
        f"Debt consolidation is the largest concentration: {money(debt['ead'])} EAD and {pct(debt['el_share'])} of expected loss. This segment needs portfolio limits or tighter sub-segmentation.",
        f"Under severe stress, expected loss increases from {money(base)} to {money(severe)}. That is a {severe / base:.2f}x loss multiple, so contingency policy should suspend auto-approval for unstable/high-risk segments.",
        f"Required pricing rises from {pct(pricing['required_rate'].min())} in low-risk grade to {pct(pricing['required_rate'].max())} in very-high-risk grade. If the market cannot bear the high-risk required rate, decline/mitigants are economically justified.",
        "This is still a public-data model: true production use would require internal DPD history, recovery cashflows, cost of funds, capital methodology, override records and independent validation.",
    ]


def write_outputs(kpis: pd.DataFrame, tables: dict[str, pd.DataFrame], conclusions: list[str]) -> None:
    kpis.to_csv(REPORTS / "31_financial_modeling_kpi_summary.csv", index=False)

    display_kpis = kpis.copy()
    display_kpis["value"] = display_kpis.apply(format_kpi_value, axis=1)
    display_kpis = display_kpis[["metric", "value", "category", "conclusion"]]

    sections = [
        "# Financial Modeling Numbers And Conclusions",
        "",
        "This report turns the Project 3 formula-first risk engine into a finance-facing view. The purpose is to show portfolio exposure, expected loss, cutoff economics, stress impact, pricing logic and management conclusions.",
        "",
        "## KPI Summary",
        "",
        md_table(display_kpis),
        "",
        "## Score Band Economics",
        "",
        md_table(tables["score"]),
        "",
        "Conclusion: score bands are economically meaningful because default rate, EL rate and required action increase as score quality weakens.",
        "",
        "## Cutoff Strategy Economics",
        "",
        md_table(tables["cutoff"]),
        "",
        "Conclusion: the 20% cutoff is a balanced portfolio policy point. It approves roughly half the portfolio while still capturing most bad accounts in review/decline.",
        "",
        "Scope consistency note: baseline expected loss of 1.53B uses full portfolio scope, while cutoff economics uses matured eligible expected loss where 100% approval equals 1.47B.",
        "",
        "## Stress Testing",
        "",
        md_table(tables["stress"]),
        "",
        "Conclusion: severe stress creates a material expected-loss uplift and should trigger contingency actions such as tighter DTI, lower limits and more manual review.",
        "",
        "## Risk-Based Pricing",
        "",
        md_table(tables["pricing"]),
        "",
        "Conclusion: pricing must increase with EL and capital cost. If required rate is not commercially feasible, decline or mitigants are more rational than approval.",
        "",
        "## IFRS 9 ECL Bridge",
        "",
        md_table(tables["ecl"]),
        "",
        "Conclusion: Stage 3 and lifetime ECL proxy are useful as a bridge, but this is not an audited IFRS 9 model because public data lacks true lifetime PD and SICR history.",
        "",
        "## Top Concentration Risks",
        "",
        md_table(tables["concentration"]),
        "",
        "Conclusion: concentration analysis prevents the portfolio from being managed only by average PD. Large EAD/EL segments need exposure limits and additional segmentation.",
        "",
        "## Worst Matured Vintages",
        "",
        md_table(tables["vintage"]),
        "",
        "Conclusion: vintage monitoring shows when booked cohorts deteriorate and is essential for post-policy monitoring.",
        "",
        "## Final Management Conclusions",
        "",
    ]
    sections.extend([f"{idx}. {text}" for idx, text in enumerate(conclusions, start=1)])
    sections.extend(
        [
            "",
            "## Interview Message",
            "",
            "The formula-first risk engine is useful because it connects credit-risk formulas to money: exposure approved, expected loss accepted, loss avoided through review/decline, stressed loss under downturn scenarios, required pricing by grade, and portfolio concentration controls.",
        ]
    )
    (REPORTS / "31_financial_modeling_numbers_and_conclusions.md").write_text("\n".join(sections), encoding="utf-8")


def format_kpi_value(row: pd.Series) -> str:
    metric = str(row["metric"]).lower()
    value = float(row["raw_value"])
    if "formula tests" in metric:
        return whole(value)
    if "ead" in metric or ("loss" in metric and "rate" not in metric) or (" el" in metric and "rate" not in metric):
        return money(value)
    if any(token in metric for token in ["rate", "auc", "ks", "capture"]):
        return pct(value)
    return whole(value)


def main() -> None:
    tables = load_tables()
    kpis = build_kpi_summary(tables)
    formatted = build_formatted_tables(tables)
    conclusions = build_conclusions(tables)
    write_outputs(kpis, formatted, conclusions)
    result = {
        "status": "complete",
        "kpi_rows": len(kpis),
        "conclusions": len(conclusions),
        "report": str(REPORTS / "31_financial_modeling_numbers_and_conclusions.md"),
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
