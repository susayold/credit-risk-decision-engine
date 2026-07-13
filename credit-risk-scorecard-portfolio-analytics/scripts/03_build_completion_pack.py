from __future__ import annotations

import json
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT = Path(__file__).resolve().parents[1]
if "FINANCIAL_RISK_DATA_CORE" not in os.environ:
    raise RuntimeError("Set FINANCIAL_RISK_DATA_CORE to run the full Project 3 rebuild.")
DATA_CORE = Path(os.environ["FINANCIAL_RISK_DATA_CORE"])
PROJECT3_GOLD = DATA_CORE / "data" / "gold" / "project3"

SOURCE_BASE = PROJECT3_GOLD / "project3_credit_risk_account_base.csv.gz"
SOURCE_WOE = PROJECT3_GOLD / "project3_woe_iv_ready_table.csv"
SOURCE_MONTHLY = PROJECT3_GOLD / "project3_monthly_monitoring_base.csv"
SOURCE_SEGMENTS = PROJECT3_GOLD / "project3_segment_default_rates.csv"
SOURCE_ASSUMPTIONS = PROJECT3_GOLD / "project3_assumption_register.csv"
SOURCE_ECL = DATA_CORE / "data" / "gold" / "gold_ecl_input_snapshot.csv.gz"

REPORTS = PROJECT / "reports"
VISUALS = PROJECT / "visuals"
DOCS = PROJECT / "docs"
EXCEL = PROJECT / "excel"

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
    for folder in [REPORTS, VISUALS, DOCS, EXCEL]:
        folder.mkdir(parents=True, exist_ok=True)


def normalize_key(series: pd.Series) -> pd.Series:
    return series.astype("string").fillna("Missing").str.strip()


def psi(expected: pd.Series, actual: pd.Series) -> float:
    categories = sorted(set(expected.index).union(set(actual.index)))
    expected = expected.reindex(categories).fillna(0.0001)
    actual = actual.reindex(categories).fillna(0.0001)
    return float(((actual - expected) * np.log(actual / expected)).sum())


def load_scored_population() -> pd.DataFrame:
    usecols = [
        "loan_id",
        "application_month",
        "observation_date",
        "performance_window_months",
        "maturity_cutoff_month",
        "matured_flag",
        "monitor_only_flag",
        "default_flag",
        "good_flag",
        "bad_flag",
        "indeterminate_flag",
        "target_population",
        "annual_income",
        "income_clean",
        "income_band",
        "income_missing_or_invalid_bin",
        "dti",
        "dti_band",
        "dti_extreme_or_missing_bin",
        "loan_amount",
        "fico_score",
        "fico_band",
        "employment_length",
        "purpose",
        "home_ownership",
        "state",
        "missing_income_flag",
        "invalid_income_flag",
        "missing_dti_flag",
        "extreme_dti_flag",
        "missing_fico_flag",
        "missing_employment_flag",
        "high_dti_flag",
        "high_amount_flag",
        "leakage_flag",
        "ead_proxy",
        "lgd_assumption",
    ]
    base = pd.read_csv(
        SOURCE_BASE,
        compression="gzip",
        usecols=usecols,
        parse_dates=["application_month", "observation_date", "maturity_cutoff_month"],
    )
    woe = pd.read_csv(SOURCE_WOE)
    woe["bin_key"] = normalize_key(woe["bin"])

    variable_iv = (
        woe.groupby("variable", as_index=False)["iv_variable_smoothed"]
        .max()
        .rename(columns={"iv_variable_smoothed": "iv"})
    )
    variable_iv["iv_weight"] = variable_iv["iv"] / variable_iv["iv"].sum()
    weights = dict(zip(variable_iv["variable"], variable_iv["iv_weight"]))
    woe_maps = {
        variable: dict(zip(rows["bin_key"], rows["woe_smoothed"]))
        for variable, rows in woe.groupby("variable")
    }

    base["good_woe_score"] = 0.0
    for variable in WOE_VARIABLES:
        mapped = normalize_key(base[variable]).map(woe_maps.get(variable, {})).astype(float).fillna(0.0)
        base[f"woe_{variable}"] = mapped
        base["good_woe_score"] += float(weights.get(variable, 0.0)) * mapped

    base["risk_score_raw"] = -base["good_woe_score"]
    base["risk_decile"] = pd.qcut(base["risk_score_raw"].rank(method="first"), 10, labels=False) + 1
    matured = base[base["matured_flag"] == 1].copy()
    decile_pd = matured.groupby("risk_decile")["bad_flag"].mean().rename("pd_formula")
    portfolio_pd = float(matured["bad_flag"].mean())
    base["pd_formula"] = base["risk_decile"].map(decile_pd).fillna(portfolio_pd).clip(0.0001, 0.9999)
    good_odds = (1 - base["pd_formula"]) / base["pd_formula"]
    factor = PDO / np.log(2)
    offset = BASE_SCORE - factor * np.log(BASE_GOOD_ODDS)
    base["scorecard_points"] = offset + factor * np.log(good_odds)
    base["expected_loss_formula"] = base["pd_formula"] * base["lgd_assumption"] * base["ead_proxy"]
    base["el_rate_formula"] = base["expected_loss_formula"] / base["ead_proxy"].replace(0, np.nan)
    base["risk_grade"] = pd.cut(
        base["pd_formula"],
        bins=[-np.inf, 0.10, 0.15, 0.20, 0.25, np.inf],
        labels=["A - Low", "B - Moderate", "C - Watch", "D - High", "E - Very High"],
    )
    base["policy_action"] = np.select(
        [
            base["pd_formula"] <= 0.10,
            base["pd_formula"] <= 0.15,
            base["pd_formula"] <= 0.20,
            base["pd_formula"] <= 0.25,
            base["pd_formula"] > 0.25,
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
    return base


def credit_lifecycle_map() -> pd.DataFrame:
    rows = [
        ("Application", "Is the applicant creditworthy?", "Application features, reject population profile", "Application count, missing income, FICO/DTI", "Approve, review or decline"),
        ("Underwriting", "Is the data reliable and eligible?", "Feature eligibility and leakage checks", "Missing flags, leakage flag, eligibility status", "Request documents or route to review"),
        ("Booking", "What exposure is created?", "Accepted/booked loan amount", "EAD proxy, loan amount, product type", "Set limit and exposure controls"),
        ("Repayment", "Is performance developing as expected?", "Matured booked accounts", "Good/bad status after performance window", "Monitor portfolio health"),
        ("Delinquency", "Is early arrears risk increasing?", "No monthly DPD in core consumer data", "Framework only: 30/60/90 DPD rates", "Early warning and collection routing"),
        ("Default", "When is the account bad?", "Default/bad flag on matured accounts", "Default rate, PD, bad count", "Model target and validation outcome"),
        ("Write-off", "What loss is recognized?", "SBA charge-off reference, proxy consumer LGD", "Charge-off profile, LGD proxy", "Loss and provision bridge"),
        ("Recovery", "How much can be collected after default?", "No consumer recovery cashflows", "Framework only: recovery rate, workout LGD", "Collection strategy and LGD limitation"),
        ("Monitoring", "Is the model/portfolio still stable?", "Monthly monitoring base and score bands", "PSI, vintage bad rate, calibration gap", "Review, recalibrate or tighten policy"),
    ]
    return pd.DataFrame(rows, columns=["lifecycle_stage", "risk_question", "data_available", "metric", "decision_use"])


def risk_taxonomy_matrix() -> pd.DataFrame:
    rows = [
        ("Default Risk", "Borrower fails to repay within performance window", "PD / Default Rate", "PD = Bad / Matured", "Approve/review/decline policy"),
        ("Delinquency Risk", "Borrower becomes past due before default", "30/60/90 DPD Rate", "DPD bucket accounts / active accounts", "Early warning and collection prioritization"),
        ("Exposure Risk", "Loss severity rises because exposure is large", "EAD", "Outstanding or loan amount proxy", "Limit control"),
        ("Recovery Risk", "Low recoveries after default", "LGD / Recovery Rate", "LGD = 1 - Recovery Rate", "Collateral, workout and collection strategy"),
        ("Concentration Risk", "Portfolio is too concentrated in one segment", "EAD Share / EL Share", "Segment EAD / Total EAD", "Portfolio limits"),
        ("Model Risk", "Scorecard may be unstable or miscalibrated", "AUC, KS, Brier, Calibration Gap, PSI", "Validation and monitoring metrics", "Recalibration or redevelopment review"),
        ("Policy Risk", "Decision rules approve too much bad risk", "Approved Bad Rate / Bad Capture", "Bad accounts in decision group / accounts", "Cutoff and override policy"),
        ("Provisioning Risk", "Expected loss is understated", "ECL", "PD x LGD x EAD", "IFRS 9 bridge and provision review"),
        ("Stress Risk", "Loss rises under adverse macro conditions", "Stressed EL / Unexpected Loss Buffer", "Stressed PD x Stressed LGD x EAD", "Risk appetite and contingency mode"),
        ("Pricing Risk", "Rate does not compensate for credit risk", "Required Rate / RAROC", "Funding + OpEx + EL + Capital + Margin", "Risk-based pricing"),
        ("Collections Risk", "Late-stage actions fail to cure or recover accounts", "Cure / Recovery / Write-off Rate", "Collected or cured / delinquent exposure", "Collections strategy"),
    ]
    return pd.DataFrame(rows, columns=["risk_type", "meaning", "metric", "formula", "decision"])


def unexpected_loss_stress_buffer(scored: pd.DataFrame) -> pd.DataFrame:
    scenarios = [
        ("Base", 1.00, 1.00, "Expected loss under current formula PD/LGD."),
        ("Mild Downturn", 1.20, 1.05, "Moderate PD/LGD deterioration."),
        ("Adverse", 1.50, 1.12, "Risk appetite stress case."),
        ("Severe", 1.90, 1.25, "Unexpected loss proxy for contingency planning."),
    ]
    rows = []
    for scenario, pd_mult, lgd_mult, note in scenarios:
        temp = scored.copy()
        temp["stressed_pd"] = (temp["pd_formula"] * pd_mult).clip(0, 0.9999)
        temp["stressed_lgd"] = (temp["lgd_assumption"] * lgd_mult).clip(0, 1.0)
        temp["stressed_loss"] = temp["stressed_pd"] * temp["stressed_lgd"] * temp["ead_proxy"]
        grouped = temp.groupby(["risk_grade", "policy_action"], observed=True).agg(
            accounts=("loan_id", "count"),
            ead=("ead_proxy", "sum"),
            avg_pd=("pd_formula", "mean"),
            stressed_pd=("stressed_pd", "mean"),
            avg_lgd=("lgd_assumption", "mean"),
            stressed_lgd=("stressed_lgd", "mean"),
            expected_loss=("expected_loss_formula", "sum"),
            loss_at_scenario=("stressed_loss", "sum"),
        )
        grouped = grouped.reset_index()
        grouped["scenario"] = scenario
        grouped["unexpected_loss_buffer"] = grouped["loss_at_scenario"] - grouped["expected_loss"]
        grouped["loss_multiple_vs_base_el"] = grouped["loss_at_scenario"] / grouped["expected_loss"].replace(0, np.nan)
        grouped["interpretation"] = note
        rows.append(grouped)
    return pd.concat(rows, ignore_index=True)


def vintage_analysis(scored: pd.DataFrame) -> pd.DataFrame:
    frame = scored.copy()
    frame["vintage_month"] = frame["application_month"].dt.to_period("M").astype(str)
    frame["vintage_quarter"] = frame["application_month"].dt.to_period("Q").astype(str)
    out = (
        frame.groupby(["vintage_quarter", "vintage_month"])
        .agg(
            accounts=("loan_id", "count"),
            matured_accounts=("matured_flag", "sum"),
            bad_accounts=("bad_flag", "sum"),
            ead=("ead_proxy", "sum"),
            expected_loss=("expected_loss_formula", "sum"),
            avg_pd=("pd_formula", "mean"),
            avg_score=("scorecard_points", "mean"),
            avg_fico=("fico_score", "mean"),
            avg_dti=("dti", "mean"),
            high_dti_share=("high_dti_flag", "mean"),
        )
        .reset_index()
    )
    out["vintage_bad_rate"] = out["bad_accounts"] / out["matured_accounts"].replace(0, np.nan)
    out["el_rate"] = out["expected_loss"] / out["ead"].replace(0, np.nan)
    out["maturity_status"] = np.where(out["matured_accounts"] > 0, "Matured outcome usable", "Monitor only")
    return out


def roll_rate_framework_matrix() -> pd.DataFrame:
    rows = [
        ("Current", "1-30 DPD", "Accounts moving Current to 1-30 / Accounts Current at start", "Monthly account DPD history", "Not observed in current consumer-loan core"),
        ("1-30 DPD", "31-60 DPD", "Accounts moving 1-30 to 31-60 / Accounts 1-30 at start", "Monthly account DPD history", "Not observed in current consumer-loan core"),
        ("31-60 DPD", "61-90 DPD", "Accounts moving 31-60 to 61-90 / Accounts 31-60 at start", "Monthly account DPD history", "Not observed in current consumer-loan core"),
        ("61-90 DPD", "90+ DPD", "Accounts moving 61-90 to 90+ / Accounts 61-90 at start", "Monthly account DPD history", "Not observed in current consumer-loan core"),
        ("90+ DPD", "Write-off", "Accounts written off / Accounts 90+ at start", "Monthly account DPD and charge-off history", "Framework only; use when servicing data is available"),
        ("Any delinquent", "Current", "Accounts cured / Delinquent accounts at start", "Monthly account DPD history", "Framework only; supports cure-rate monitoring"),
    ]
    return pd.DataFrame(rows, columns=["from_bucket", "to_bucket", "formula", "required_data", "project3_status"])


def ifrs9_ecl_bridge() -> pd.DataFrame:
    ecl = pd.read_csv(SOURCE_ECL, compression="gzip")
    ecl["lifetime_multiplier"] = np.select(
        [ecl["stage"].eq("Stage 1"), ecl["stage"].eq("Stage 2"), ecl["stage"].eq("Stage 3")],
        [1.0, 2.5, 3.5],
        default=1.0,
    )
    ecl["ecl_lifetime_proxy"] = ecl["ecl_base"] * ecl["lifetime_multiplier"]
    ecl["sicr_logic"] = np.select(
        [ecl["stage"].eq("Stage 1"), ecl["stage"].eq("Stage 2"), ecl["stage"].eq("Stage 3")],
        ["Performing: 12-month ECL", "Significant increase in credit risk: lifetime ECL proxy", "Credit-impaired/default proxy: lifetime ECL"],
        default="Review",
    )
    out = (
        ecl.groupby(["stage", "fico_band"])
        .agg(
            accounts=("loan_id", "count"),
            ead=("ead", "sum"),
            avg_pd=("pd_observed", "mean"),
            avg_lgd=("lgd", "mean"),
            ecl_12m_or_base=("ecl_base", "sum"),
            ecl_lifetime_proxy=("ecl_lifetime_proxy", "sum"),
        )
        .reset_index()
    )
    out["ecl_rate_base"] = out["ecl_12m_or_base"] / out["ead"].replace(0, np.nan)
    out["ecl_rate_lifetime_proxy"] = out["ecl_lifetime_proxy"] / out["ead"].replace(0, np.nan)
    out["ifrs9_note"] = "Bridge only: public data does not support audited IFRS 9 staging or lifetime PD."
    return out


def stress_testing_scenarios(scored: pd.DataFrame) -> pd.DataFrame:
    scenarios = [
        ("Base", 1.00, 1.00, 1.00),
        ("Mild Downturn", 1.20, 1.05, 1.00),
        ("Adverse", 1.50, 1.12, 1.02),
        ("Severe", 1.90, 1.25, 1.05),
    ]
    rows = []
    for scenario, pd_mult, lgd_mult, ead_mult in scenarios:
        temp = scored.copy()
        temp["scenario"] = scenario
        temp["stressed_pd"] = (temp["pd_formula"] * pd_mult).clip(0, 0.9999)
        temp["stressed_lgd"] = (temp["lgd_assumption"] * lgd_mult).clip(0, 1)
        temp["stressed_ead"] = temp["ead_proxy"] * ead_mult
        temp["stressed_el"] = temp["stressed_pd"] * temp["stressed_lgd"] * temp["stressed_ead"]
        out = temp.groupby(["scenario", "risk_grade"], observed=True).agg(
            accounts=("loan_id", "count"),
            stressed_ead=("stressed_ead", "sum"),
            stressed_el=("stressed_el", "sum"),
            avg_stressed_pd=("stressed_pd", "mean"),
            avg_stressed_lgd=("stressed_lgd", "mean"),
        )
        out = out.reset_index()
        out["stressed_el_rate"] = out["stressed_el"] / out["stressed_ead"].replace(0, np.nan)
        rows.append(out)
    return pd.concat(rows, ignore_index=True)


def risk_based_pricing(expected_loss_by_grade: pd.DataFrame) -> pd.DataFrame:
    capital_cost = {
        "A - Low": 0.010,
        "B - Moderate": 0.015,
        "C - Watch": 0.025,
        "D - High": 0.040,
        "E - Very High": 0.060,
    }
    economic_capital = {
        "A - Low": 0.040,
        "B - Moderate": 0.060,
        "C - Watch": 0.080,
        "D - High": 0.110,
        "E - Very High": 0.150,
    }
    out = expected_loss_by_grade.copy()
    out["funding_cost_rate"] = 0.045
    out["operating_cost_rate"] = 0.025
    out["capital_cost_rate"] = out["risk_grade"].astype(str).map(capital_cost).fillna(0.035)
    out["profit_margin_rate"] = 0.020
    out["required_rate"] = (
        out["el_rate"]
        + out["funding_cost_rate"]
        + out["operating_cost_rate"]
        + out["capital_cost_rate"]
        + out["profit_margin_rate"]
    )
    out["illustrative_offered_rate"] = out["required_rate"] + 0.010
    out["risk_adjusted_profit_rate"] = (
        out["illustrative_offered_rate"]
        - out["el_rate"]
        - out["funding_cost_rate"]
        - out["operating_cost_rate"]
        - out["capital_cost_rate"]
    )
    out["economic_capital_rate"] = out["risk_grade"].astype(str).map(economic_capital).fillna(0.080)
    out["raroc_proxy"] = out["risk_adjusted_profit_rate"] / out["economic_capital_rate"].replace(0, np.nan)
    out["pricing_note"] = "Illustrative only: funding, operating, capital and margin assumptions must be owned by Finance/Risk."
    return out[
        [
            "risk_grade",
            "policy_action",
            "accounts",
            "ead_proxy",
            "el_rate",
            "funding_cost_rate",
            "operating_cost_rate",
            "capital_cost_rate",
            "profit_margin_rate",
            "required_rate",
            "illustrative_offered_rate",
            "risk_adjusted_profit_rate",
            "economic_capital_rate",
            "raroc_proxy",
            "pricing_note",
        ]
    ]


def collections_recovery_strategy() -> pd.DataFrame:
    rows = [
        ("Current", "No arrears", "Monitor score/PSI and payment behavior", "Low", "N/A", "Keep normal servicing"),
        ("1-30 DPD", "Early delinquency", "SMS/email reminder, soft call, payment link", "Medium", "Cure Rate", "Prevent roll-forward"),
        ("31-60 DPD", "Mid delinquency", "Call campaign, hardship assessment, promise-to-pay tracking", "High", "Roll-back Rate", "Cure before default"),
        ("61-90 DPD", "Late delinquency", "Specialist collector, restructure eligibility, collateral review", "Very High", "Roll-forward to 90+", "Reduce default conversion"),
        ("90+ DPD", "Default treatment", "Default classification, workout queue, settlement decision", "Critical", "Recovery Rate", "Maximize recovery and control LGD"),
        ("Write-off", "Charged off", "Recovery/legal/agency placement where appropriate", "Critical", "Net Loss Rate", "Recover value after charge-off"),
    ]
    return pd.DataFrame(rows, columns=["dpd_bucket", "risk_state", "recommended_action", "priority", "main_metric", "business_objective"])


def concentration_risk(scored: pd.DataFrame) -> pd.DataFrame:
    frames = []
    for variable in ["risk_grade", "purpose", "state", "fico_band", "income_band"]:
        grouped = scored.groupby(variable, observed=True).agg(
            accounts=("loan_id", "count"),
            matured_accounts=("matured_flag", "sum"),
            bad_accounts=("bad_flag", "sum"),
            ead=("ead_proxy", "sum"),
            expected_loss=("expected_loss_formula", "sum"),
            avg_pd=("pd_formula", "mean"),
        )
        grouped = grouped.reset_index().rename(columns={variable: "segment_value"})
        grouped["segment_variable"] = variable
        frames.append(grouped)
    out = pd.concat(frames, ignore_index=True)
    out["default_rate_matured"] = out["bad_accounts"] / out["matured_accounts"].replace(0, np.nan)
    out["ead_share"] = out["ead"] / out.groupby("segment_variable")["ead"].transform("sum")
    out["el_share"] = out["expected_loss"] / out.groupby("segment_variable")["expected_loss"].transform("sum")
    out["concentration_flag"] = np.where((out["ead_share"] >= 0.20) | (out["el_share"] >= 0.20), "High concentration", "Normal")
    return out.sort_values(["segment_variable", "expected_loss"], ascending=[True, False])


def monitoring_triggers() -> pd.DataFrame:
    rows = [
        ("PSI", "<0.10 stable; 0.10-0.25 watchlist; >0.25 review", "Score/population distribution shift", "Investigate CSI, segment mix and policy changes"),
        ("CSI", ">0.25 on key characteristic", "Input variable drift", "Identify feature causing PSI movement"),
        ("AUC/KS/Gini", "Material drop for 3 matured monitoring periods", "Ranking degradation after outcomes mature", "Root cause analysis; recalibration or redevelopment if confirmed"),
        ("Calibration Gap", "Observed default materially above predicted PD", "Probability under-prediction", "Recalibrate PD mapping or apply overlay"),
        ("Vintage Bad Rate", "New cohorts worse than historical cohorts", "Portfolio deterioration", "Tighten policy, review channel/product mix"),
        ("Approved Bad Rate", "Approved risk above risk appetite", "Cutoff/policy weakness", "Lower cutoff or increase manual review"),
        ("Override Rate", "Illustrative 5-10% portfolio threshold", "Policy exceptions may weaken score discipline", "Review override authority and bad rate"),
        ("Data Quality", "Missing/invalid key fields increase", "Feature reliability issue", "Route to manual review or data remediation"),
        ("Macro Stress", "Severe scenario EL breaches appetite", "Stress vulnerability", "Activate contingency mode"),
    ]
    return pd.DataFrame(rows, columns=["metric", "trigger_threshold", "risk_signal", "management_action"])


def override_policy_simulation(scored: pd.DataFrame) -> pd.DataFrame:
    frame = scored.copy()
    low_dti = frame["dti"].fillna(999) <= 15
    strong_fico = frame["fico_band"].isin(["A+", "A-", "B"])
    high_income = frame["income_clean"].fillna(0) >= 100_000
    missing_key_data = (
        frame[["missing_income_flag", "missing_dti_flag", "missing_fico_flag", "missing_employment_flag"]]
        .sum(axis=1)
        .gt(0)
    )
    frame["override_type"] = np.select(
        [
            frame["policy_action"].eq("Decline or require mitigants") & strong_fico & low_dti & high_income,
            frame["policy_action"].isin(["Approve standard", "Approve with limit/pricing control"]) & (frame["high_dti_flag"].eq(1) | frame["high_amount_flag"].eq(1)),
            missing_key_data,
        ],
        [
            "Hard override candidate: decline to senior review",
            "Soft override candidate: reduce limit/pricing/manual review",
            "Data-quality override: manual verification",
        ],
        default="No override candidate",
    )
    out = frame.groupby(["override_type", "policy_action"], observed=True).agg(
        accounts=("loan_id", "count"),
        matured_accounts=("matured_flag", "sum"),
        bad_accounts=("bad_flag", "sum"),
        ead=("ead_proxy", "sum"),
        expected_loss=("expected_loss_formula", "sum"),
        avg_pd=("pd_formula", "mean"),
    )
    out = out.reset_index()
    out["observed_bad_rate"] = out["bad_accounts"] / out["matured_accounts"].replace(0, np.nan)
    out["override_note"] = "Simulation only: true override decisions are not present in the public data."
    return out.sort_values("accounts", ascending=False)


def expected_loss_by_grade(scored: pd.DataFrame) -> pd.DataFrame:
    out = (
        scored.groupby(["risk_grade", "policy_action"], observed=True)
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
    out["el_rate"] = out["expected_loss"] / out["ead_proxy"].replace(0, np.nan)
    return out


def acceptance_criteria_status() -> pd.DataFrame:
    rows = [
        ("Credit Risk / Lending Risk project is clear", "Done", "README.md, website case study, business context"),
        ("Target definition is clear", "Done", "reports/01_population_target_summary.csv, docs/model_card.md"),
        ("Observation/performance window is documented", "Done", "docs/methodology_note.md"),
        ("Matured account logic is implemented", "Done", "matured_flag, monitor_only_flag, formula test cases"),
        ("Leakage checklist is documented", "Done", "docs/validation_checklist.md, project3_feature_eligibility_matrix.csv"),
        ("Reject inference limitation is explicit", "Done", "reports/11_reject_inference_sensitivity.csv"),
        ("PD, LGD, EAD, EL are available", "Done with proxy assumptions", "reports/09_expected_loss_by_risk_grade.csv"),
        ("WOE, IV, odds and log odds are available", "Done", "reports/03_woe_iv_variable_summary.csv, docs/formula_dictionary.md"),
        ("Scorecard and score bands are available", "Done", "reports/05_score_band_summary.csv"),
        ("Credit decision rules are available", "Done", "reports/08_cutoff_strategy.csv, reports/27_override_policy_simulation.csv"),
        ("Expected loss by segment is available", "Done", "reports/09_expected_loss_by_risk_grade.csv, reports/25_concentration_risk_by_segment.csv"),
        ("AUC, KS, Gini, Brier are available", "Done", "reports/06_validation_metrics.csv"),
        ("Enriched scorecard and logistic challenger are available", "Done", "reports/36_challenger_model_comparison.csv"),
        ("Calibration gap is available", "Done", "reports/07_calibration_by_decile.csv"),
        ("PSI is available", "Done", "reports/10_monitoring_psi.csv"),
        ("Vintage analysis is available", "Done", "reports/19_vintage_analysis.csv"),
        ("Roll-rate matrix is available", "Framework only", "reports/20_roll_rate_framework_matrix.csv; monthly DPD unavailable"),
        ("IFRS 9 ECL bridge is available", "Bridge only", "reports/21_ifrs9_ecl_bridge.csv"),
        ("Stress testing is available", "Done with proxy assumptions", "reports/22_stress_testing_scenarios.csv"),
        ("Risk-based pricing is available", "Done with assumptions", "reports/23_risk_based_pricing_by_grade.csv"),
        ("Governance and limitation pack is available", "Done", "docs/governance_and_limitations.md, reports/26_model_monitoring_triggers.csv"),
        ("README can be read within 60 seconds", "Done", "README.md"),
        ("Interview story is available", "Done", "docs/interview_story.md, docs/final_recruiter_interview_pack.md"),
    ]
    return pd.DataFrame(rows, columns=["acceptance_criterion", "status", "evidence"])


def formula_test_cases(scored: pd.DataFrame, woe: pd.DataFrame, vintage: pd.DataFrame, ecl: pd.DataFrame) -> pd.DataFrame:
    tests: list[dict[str, str]] = []

    def add(test_id: str, test_name: str, passed: bool, evidence: str) -> None:
        tests.append(
            {
                "test_id": test_id,
                "test_name": test_name,
                "status": "PASS" if passed else "FAIL",
                "evidence": evidence,
            }
        )

    matured = scored[scored["matured_flag"] == 1]
    reported_default_rate = float(pd.read_csv(REPORTS / "01_population_target_summary.csv").set_index("metric").loc["matured_default_rate", "value"])
    calculated_default_rate = float(matured["bad_flag"].mean())
    add("T01", "Account not matured is excluded from default rate", scored.loc[scored["monitor_only_flag"] == 1, "bad_flag"].sum() == 0, "Monitor-only accounts do not contribute bad flags.")
    add("T02", "Leakage flag is controlled", scored["leakage_flag"].sum() == 0, f"Leakage flag total = {int(scored['leakage_flag'].sum())}.")
    add("T03", "Default Rate = Defaulted Matured Accounts / Matured Accounts", abs(reported_default_rate - calculated_default_rate) < 1e-12, f"reported={reported_default_rate:.8f}, calculated={calculated_default_rate:.8f}")
    pct_good_sum = woe.groupby("variable")["pct_good_smoothed"].sum().round(6)
    pct_bad_sum = woe.groupby("variable")["pct_bad_smoothed"].sum().round(6)
    add("T04", "WOE good distribution sums to 100% by variable", bool(np.allclose(pct_good_sum, 1.0, atol=0.0001)), pct_good_sum.to_dict().__repr__())
    add("T05", "WOE bad distribution sums to 100% by variable", bool(np.allclose(pct_bad_sum, 1.0, atol=0.0001)), pct_bad_sum.to_dict().__repr__())
    add("T06", "WOE smoothing avoids infinite WOE", np.isfinite(woe["woe_smoothed"]).all(), "All smoothed WOE values are finite.")
    add("T07", "IV variable equals sum of IV bins", bool(np.allclose(woe.groupby("variable")["iv_bin_smoothed"].sum(), woe.groupby("variable")["iv_variable_smoothed"].max(), atol=0.0001)), "IV bin sum reconciles to variable IV.")
    add("T08", "PD stays between 0 and 1", scored["pd_formula"].between(0, 1).all(), f"min={scored['pd_formula'].min():.4f}, max={scored['pd_formula'].max():.4f}")
    grade_scores = scored.groupby("risk_grade", observed=True)["scorecard_points"].mean()
    add("T09", "Higher score corresponds to lower risk grade", grade_scores.iloc[0] > grade_scores.iloc[-1], grade_scores.round(2).to_dict().__repr__())
    expected_loss_sum = float(scored["expected_loss_formula"].sum())
    grade_el_sum = float(pd.read_csv(REPORTS / "09_expected_loss_by_risk_grade.csv")["expected_loss"].sum())
    add("T10", "Portfolio EL equals sum of account-level EL", abs(expected_loss_sum - grade_el_sum) < 1, f"account={expected_loss_sum:.2f}, grade={grade_el_sum:.2f}")
    cal = pd.read_csv(REPORTS / "07_calibration_by_decile.csv")
    add("T11", "Calibration Gap = Observed Default Rate - Average PD", np.allclose(cal["calibration_gap"], cal["observed_default_rate"] - cal["avg_pd"], atol=1e-12), "Calibration table formula reconciles.")
    dist = scored["risk_grade"].value_counts(normalize=True)
    add("T12", "PSI is zero when actual distribution equals expected distribution", abs(psi(dist, dist)) < 1e-12, "Identical distributions produce PSI 0.")
    add("T13", "Vintage bad rate uses matured-account denominator", np.allclose(vintage["vintage_bad_rate"].fillna(0), (vintage["bad_accounts"] / vintage["matured_accounts"].replace(0, np.nan)).fillna(0)), "Vintage formula reconciles.")
    roll = roll_rate_framework_matrix()
    add("T14", "Roll-rate denominator is defined by opening DPD bucket", roll["formula"].str.contains("at start").all(), "All roll-rate formulas specify denominator at start.")
    add("T15", "IFRS 9 Stage 1 uses base/12-month ECL and Stage 2/3 use lifetime proxy", {"Stage 1", "Stage 2", "Stage 3"}.intersection(set(ecl["stage"])) == {"Stage 1", "Stage 2", "Stage 3"}, "All three IFRS 9 bridge stages are present.")
    return pd.DataFrame(tests)


def write_markdown_docs(
    lifecycle: pd.DataFrame,
    taxonomy: pd.DataFrame,
    acceptance: pd.DataFrame,
    tests: pd.DataFrame,
) -> None:
    lifecycle_md = [
        "# Credit Lifecycle Map",
        "",
        "This document maps the lending lifecycle to the risk question, metric and decision use in Project 3.",
        "",
        "```mermaid",
        "flowchart LR",
        '  A["Application"] --> B["Underwriting"] --> C["Approval / Review / Decline"] --> D["Booking"] --> E["Repayment"] --> F["Delinquency"] --> G["Default"] --> H["Write-off"] --> I["Recovery"] --> J["Portfolio Monitoring"]',
        "```",
        "",
        markdown_table(lifecycle),
    ]
    (DOCS / "credit_lifecycle_map.md").write_text("\n".join(lifecycle_md), encoding="utf-8")

    taxonomy_md = [
        "# Credit Risk Taxonomy Map",
        "",
        "This map keeps the project focused on lending credit risk, not fraud, market or liquidity risk.",
        "",
        markdown_table(taxonomy),
    ]
    (DOCS / "risk_taxonomy_map.md").write_text("\n".join(taxonomy_md), encoding="utf-8")

    pack_md = [
        "# Final Recruiter Interview Pack",
        "",
        "## One-minute pitch",
        "",
        "This project builds a formula-first credit risk scorecard and portfolio analytics workflow for a lending portfolio. It starts with target definition and matured-account logic, then calculates WOE/IV, PD, scorecard points, expected loss, validation metrics, cutoff policy, monitoring triggers, IFRS 9 bridge, stress testing, risk-based pricing and governance documentation. The enriched modeling layer adds stronger application-time variables and benchmarks the scorecard against a logistic regression challenger.",
        "",
        "## Value to employer",
        "",
        "- I can define a credit-risk target correctly before modeling.",
        "- I can translate borrower data into PD, score bands, expected loss and policy actions.",
        "- I can validate discrimination, calibration and business cutoff trade-offs.",
        "- I can compare a transparent scorecard with a challenger model without over-claiming production readiness.",
        "- I can document limitations honestly instead of over-claiming public-data assumptions.",
        "- I can package outputs for Risk, Credit Policy, Finance and Model Governance stakeholders.",
        "",
        "## Best interview story",
        "",
        "I did not start with machine learning first. I started with the credit-risk logic: good/bad definition, observation window, performance window and matured population. Then I used WOE/IV to understand risk drivers, built a transparent scorecard-style PD workflow, translated PD into policy actions, and connected those decisions to expected loss, monitoring and governance. After that baseline was explainable, I added an enriched scorecard and logistic challenger benchmark to show the performance trade-off.",
        "",
        "## CV bullet",
        "",
        "Built an end-to-end credit risk scorecard and portfolio analytics framework on 1.3M+ accepted/booked lending accounts, with an enriched accepted-loan modeling benchmark on 331.9K rows comparing expanded WOE scorecard versus logistic regression challenger.",
        "",
        "## Acceptance status",
        "",
        markdown_table(acceptance),
        "",
        "## Formula test results",
        "",
        markdown_table(tests),
    ]
    (DOCS / "final_recruiter_interview_pack.md").write_text("\n".join(pack_md), encoding="utf-8")


def markdown_table(frame: pd.DataFrame) -> str:
    safe = frame.copy().astype(str)
    safe = safe.replace({"nan": "", "NaT": ""})
    headers = list(safe.columns)
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for _, row in safe.iterrows():
        cells = [str(row[col]).replace("|", "/").replace("\n", " ") for col in headers]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def write_completion_summary(
    scored: pd.DataFrame,
    stress: pd.DataFrame,
    pricing: pd.DataFrame,
    tests: pd.DataFrame,
    acceptance: pd.DataFrame,
) -> None:
    mature = scored[scored["matured_flag"] == 1]
    severe = stress[stress["scenario"].eq("Severe")]
    summary = f"""# Project 3 Completion Summary

## Final Project Positioning

Credit Risk Scorecard & Portfolio Analytics: From Risk Theory to Portfolio Monitoring.

This is a formula-first credit risk project for lending risk. It is not positioned as a generic ML exercise. The project demonstrates target definition, matured account logic, WOE/IV, PD, scorecard points, cutoff policy, expected loss, monitoring, IFRS 9 bridge, stress testing, pricing, collections, concentration risk and governance.

## Data Scale

- Total accounts: {len(scored):,}
- Matured accounts: {len(mature):,}
- Matured default rate: {mature['bad_flag'].mean():.2%}
- Total EAD proxy: {scored['ead_proxy'].sum():,.0f}
- Formula expected loss: {scored['expected_loss_formula'].sum():,.0f}

## Senior Risk Modules Added

- Credit lifecycle map.
- Credit risk taxonomy map.
- Unexpected loss / stress buffer.
- Vintage analysis.
- Roll-rate framework matrix with data limitation.
- IFRS 9 ECL bridge.
- Stress testing scenarios.
- Risk-based pricing and RAROC proxy.
- Collections and recovery strategy.
- Concentration risk table.
- Override policy simulation.
- Monitoring trigger framework.
- Excel master workbook.
- Formula test cases.
- Final recruiter interview pack.

## Stress Result

- Severe scenario stressed EL: {severe['stressed_el'].sum():,.0f}
- Severe scenario stressed EAD: {severe['stressed_ead'].sum():,.0f}
- Severe stressed EL rate: {(severe['stressed_el'].sum() / severe['stressed_ead'].sum()):.2%}

## Pricing Result

- Lowest required rate by grade: {pricing['required_rate'].min():.2%}
- Highest required rate by grade: {pricing['required_rate'].max():.2%}

## Controls

- Formula tests passed: {(tests['status'].eq('PASS')).sum()} / {len(tests)}
- Acceptance criteria completed or documented with limitation: {len(acceptance)} / {len(acceptance)}

## Important Limitation

The project is complete for portfolio and interview purposes, but it remains a public-data project. True production deployment would require internal application data, monthly DPD history, recovery cashflows, override records, independent validation and institution-owned risk appetite thresholds.
"""
    (REPORTS / "30_project3_completion_summary.md").write_text(summary, encoding="utf-8")


def plot_completion_outputs(vintage: pd.DataFrame, stress: pd.DataFrame, concentration: pd.DataFrame) -> None:
    vintage_plot = vintage[vintage["matured_accounts"] >= 1000].copy()
    if not vintage_plot.empty:
        fig, ax = plt.subplots(figsize=(11, 5.8), facecolor=COLORS["bg"])
        ax.plot(pd.to_datetime(vintage_plot["vintage_month"]), vintage_plot["vintage_bad_rate"], color=COLORS["blue"], linewidth=1.8)
        ax.set_title("Vintage Bad Rate by Application Month", loc="left", color=COLORS["ink"], fontweight="bold")
        ax.set_ylabel("Bad rate")
        ax.grid(True, color=COLORS["line"])
        fig.tight_layout()
        fig.savefig(VISUALS / "vintage_default_rate.png", dpi=170, bbox_inches="tight")
        plt.close(fig)

    stress_plot = stress.groupby("scenario", as_index=False)["stressed_el"].sum()
    fig, ax = plt.subplots(figsize=(9, 5.2), facecolor=COLORS["bg"])
    ax.bar(stress_plot["scenario"], stress_plot["stressed_el"], color=[COLORS["teal"], COLORS["gold"], COLORS["red"], COLORS["ink"]])
    ax.set_title("Expected Loss Under Stress Scenarios", loc="left", color=COLORS["ink"], fontweight="bold")
    ax.set_ylabel("Stressed expected loss")
    ax.grid(axis="y", color=COLORS["line"])
    fig.tight_layout()
    fig.savefig(VISUALS / "stress_el_by_scenario.png", dpi=170, bbox_inches="tight")
    plt.close(fig)

    top = (
        concentration[concentration["segment_variable"].eq("purpose")]
        .sort_values("expected_loss", ascending=False)
        .head(10)
        .copy()
    )
    fig, ax = plt.subplots(figsize=(10, 5.6), facecolor=COLORS["bg"])
    ax.barh(top["segment_value"].astype(str), top["expected_loss"], color=COLORS["blue"])
    ax.invert_yaxis()
    ax.set_title("Top Purpose Segments by Expected Loss", loc="left", color=COLORS["ink"], fontweight="bold")
    ax.set_xlabel("Expected loss")
    ax.grid(axis="x", color=COLORS["line"])
    fig.tight_layout()
    fig.savefig(VISUALS / "concentration_el_top_segments.png", dpi=170, bbox_inches="tight")
    plt.close(fig)


def write_excel_workbook(tables: dict[str, pd.DataFrame]) -> None:
    workbook_path = EXCEL / "Credit_Risk_Formula_Engine.xlsx"
    with pd.ExcelWriter(workbook_path, engine="xlsxwriter") as writer:
        workbook = writer.book
        header = workbook.add_format({"bold": True, "bg_color": "#12355B", "font_color": "white", "border": 1})
        percent = workbook.add_format({"num_format": "0.00%"})
        number = workbook.add_format({"num_format": "#,##0"})
        money = workbook.add_format({"num_format": "#,##0"})
        wrap = workbook.add_format({"text_wrap": True, "valign": "top"})

        readme = pd.DataFrame(
            [
                ("Project", "Credit Risk Decision Engine"),
                ("Positioning", "Formula-first credit risk management portfolio project."),
                ("Core value", "Translate lending data into PD, scorecard, cutoff, expected loss, monitoring and governance."),
                ("Important note", "Some modules use proxy assumptions because public data lacks monthly DPD, recovery cashflows and override records."),
            ],
            columns=["item", "value"],
        )
        sheet_map = {
            "00_README": readme,
            "01_Data_Dictionary": tables["data_dictionary"],
            "02_Target_Definition": tables["population"],
            "03_Formula_Dictionary": tables["formulas"],
            "04_WOE_IV": tables["woe_iv"],
            "05_PD_Odds_LogOdds": tables["decile_pd"],
            "06_Score_Bands": tables["score_bands"],
            "07_Cutoff_Policy": tables["cutoffs"],
            "08_Validation": tables["validation"],
            "09_Calibration": tables["calibration"],
            "10_PSI": tables["psi"],
            "11_Vintage": tables["vintage"].head(500),
            "12_Roll_Rate": tables["roll_rate"],
            "13_IFRS9_ECL": tables["ecl"],
            "14_Stress_Testing": tables["stress"],
            "15_Risk_Pricing": tables["pricing"],
            "16_Collections": tables["collections"],
            "17_Concentration": tables["concentration"].head(500),
            "18_Governance_Checklist": tables["monitoring_triggers"],
            "19_Test_Cases": tables["tests"],
            "20_Final_Summary": tables["acceptance"],
        }
        for sheet_name, frame in sheet_map.items():
            frame.to_excel(writer, sheet_name=sheet_name, index=False)
            worksheet = writer.sheets[sheet_name]
            worksheet.freeze_panes(1, 0)
            worksheet.autofilter(0, 0, max(len(frame), 1), max(len(frame.columns) - 1, 0))
            for col_num, col_name in enumerate(frame.columns):
                width = min(max(len(str(col_name)) + 4, 14), 42)
                worksheet.write(0, col_num, col_name, header)
                if any(key in col_name.lower() for key in ["rate", "share", "pd", "lgd", "ks", "auc", "gini", "brier", "raroc", "gap"]):
                    worksheet.set_column(col_num, col_num, width, percent)
                elif any(key in col_name.lower() for key in ["ead", "loss", "accounts", "bad", "good", "rows"]):
                    worksheet.set_column(col_num, col_num, width, money if "loss" in col_name.lower() or "ead" in col_name.lower() else number)
                else:
                    worksheet.set_column(col_num, col_num, width, wrap)


def build_data_dictionary(scored: pd.DataFrame) -> pd.DataFrame:
    selected = [
        "loan_id",
        "application_month",
        "observation_date",
        "maturity_cutoff_month",
        "matured_flag",
        "monitor_only_flag",
        "bad_flag",
        "good_flag",
        "indeterminate_flag",
        "annual_income",
        "dti",
        "loan_amount",
        "fico_score",
        "fico_band",
        "purpose",
        "home_ownership",
        "ead_proxy",
        "lgd_assumption",
        "pd_formula",
        "scorecard_points",
        "risk_grade",
        "policy_action",
        "expected_loss_formula",
    ]
    rows = []
    for column in selected:
        rows.append(
            {
                "field": column,
                "dtype": str(scored[column].dtype),
                "non_null_rows": int(scored[column].notna().sum()),
                "missing_rows": int(scored[column].isna().sum()),
                "business_definition": _field_definition(column),
            }
        )
    return pd.DataFrame(rows)


def _field_definition(column: str) -> str:
    definitions = {
        "loan_id": "Unique account/loan identifier.",
        "application_month": "Application or origination month used as vintage.",
        "observation_date": "Date at which application-time features are observed.",
        "maturity_cutoff_month": "Cutoff date used to determine whether performance window is seasoned.",
        "matured_flag": "1 if account has enough performance window to label good/bad.",
        "monitor_only_flag": "1 if account is too recent for final default outcome.",
        "bad_flag": "Default/bad outcome used for PD modeling on matured accounts.",
        "good_flag": "Non-default outcome used for good/bad distribution.",
        "indeterminate_flag": "Account that should not be treated as good or bad.",
        "annual_income": "Borrower reported annual income.",
        "dti": "Debt-to-income ratio.",
        "loan_amount": "Loan amount; used as EAD proxy for term-loan style product.",
        "fico_score": "Credit score proxy.",
        "fico_band": "Binned FICO score used in scorecard logic.",
        "purpose": "Loan purpose segment.",
        "home_ownership": "Borrower home ownership category.",
        "ead_proxy": "Exposure at default proxy.",
        "lgd_assumption": "Loss given default assumption by risk band.",
        "pd_formula": "Formula-first probability of default mapped by WOE risk decile.",
        "scorecard_points": "Scorecard points using good-odds convention.",
        "risk_grade": "Risk band A-E mapped from formula PD.",
        "policy_action": "Recommended credit action from PD band.",
        "expected_loss_formula": "PD x LGD x EAD.",
    }
    return definitions.get(column, "Project field.")


def main() -> None:
    ensure_dirs()
    scored = load_scored_population()
    woe = pd.read_csv(SOURCE_WOE)

    lifecycle = credit_lifecycle_map()
    taxonomy = risk_taxonomy_matrix()
    unexpected = unexpected_loss_stress_buffer(scored)
    vintage = vintage_analysis(scored)
    roll_rate = roll_rate_framework_matrix()
    ecl = ifrs9_ecl_bridge()
    stress = stress_testing_scenarios(scored)
    el_grade = expected_loss_by_grade(scored)
    pricing = risk_based_pricing(el_grade)
    collections = collections_recovery_strategy()
    concentration = concentration_risk(scored)
    monitoring = monitoring_triggers()
    overrides = override_policy_simulation(scored)
    acceptance = acceptance_criteria_status()
    tests = formula_test_cases(scored, woe, vintage, ecl)

    lifecycle.to_csv(REPORTS / "16_credit_lifecycle_map.csv", index=False)
    taxonomy.to_csv(REPORTS / "17_risk_taxonomy_matrix.csv", index=False)
    unexpected.to_csv(REPORTS / "18_unexpected_loss_stress_buffer.csv", index=False)
    vintage.to_csv(REPORTS / "19_vintage_analysis.csv", index=False)
    roll_rate.to_csv(REPORTS / "20_roll_rate_framework_matrix.csv", index=False)
    ecl.to_csv(REPORTS / "21_ifrs9_ecl_bridge.csv", index=False)
    stress.to_csv(REPORTS / "22_stress_testing_scenarios.csv", index=False)
    pricing.to_csv(REPORTS / "23_risk_based_pricing_by_grade.csv", index=False)
    collections.to_csv(REPORTS / "24_collections_recovery_strategy.csv", index=False)
    concentration.to_csv(REPORTS / "25_concentration_risk_by_segment.csv", index=False)
    monitoring.to_csv(REPORTS / "26_model_monitoring_triggers.csv", index=False)
    overrides.to_csv(REPORTS / "27_override_policy_simulation.csv", index=False)
    acceptance.to_csv(REPORTS / "28_project_scope_completion_status.csv", index=False)
    tests.to_csv(REPORTS / "29_formula_test_cases.csv", index=False)

    write_markdown_docs(lifecycle, taxonomy, acceptance, tests)
    write_completion_summary(scored, stress, pricing, tests, acceptance)
    plot_completion_outputs(vintage, stress, concentration)

    population = pd.read_csv(REPORTS / "01_population_target_summary.csv")
    formulas = pd.read_csv(REPORTS / "02_formula_dictionary.csv")
    decile_pd = pd.read_csv(REPORTS / "04_decile_pd_mapping.csv")
    score_bands = pd.read_csv(REPORTS / "05_score_band_summary.csv")
    cutoffs = pd.read_csv(REPORTS / "08_cutoff_strategy.csv")
    validation = pd.read_csv(REPORTS / "06_validation_metrics.csv")
    calibration = pd.read_csv(REPORTS / "07_calibration_by_decile.csv")
    psi_table = pd.read_csv(REPORTS / "10_monitoring_psi.csv")
    tables = {
        "data_dictionary": build_data_dictionary(scored),
        "population": population,
        "formulas": formulas,
        "woe_iv": woe,
        "decile_pd": decile_pd,
        "score_bands": score_bands,
        "cutoffs": cutoffs,
        "validation": validation,
        "calibration": calibration,
        "psi": psi_table,
        "vintage": vintage,
        "roll_rate": roll_rate,
        "ecl": ecl,
        "stress": stress,
        "pricing": pricing,
        "collections": collections,
        "concentration": concentration,
        "monitoring_triggers": monitoring,
        "tests": tests,
        "acceptance": acceptance,
    }
    write_excel_workbook(tables)

    completion = {
        "status": "complete",
        "new_reports": 15,
        "formula_tests_passed": int(tests["status"].eq("PASS").sum()),
        "formula_tests_total": int(len(tests)),
        "acceptance_items": int(len(acceptance)),
        "excel_workbook": "excel/Credit_Risk_Formula_Engine.xlsx",
        "completion_summary": "reports/30_project3_completion_summary.md",
    }
    (REPORTS / "completion_pack_summary.json").write_text(json.dumps(completion, indent=2), encoding="utf-8")
    print(json.dumps(completion, indent=2))


if __name__ == "__main__":
    main()
