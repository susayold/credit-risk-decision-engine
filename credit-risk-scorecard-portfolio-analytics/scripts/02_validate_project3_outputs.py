from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


PROJECT = Path(__file__).resolve().parents[1]


REQUIRED_FILES = [
    "README.md",
    "index.html",
    "DATA_ACCESS.md",
    "ARTIFACT_INDEX.md",
    "requirements.txt",
    "scripts/01_build_formula_first_engine.py",
    "reports/formula_engine_summary.json",
    "scripts/03_build_completion_pack.py",
    "scripts/04_build_financial_modeling_summary.py",
    "scripts/06_quick_review_from_sample.py",
    "scripts/07_package_portable_zip.py",
    "scripts/08_build_enriched_scorecard_challenger.py",
    "reports/completion_pack_summary.json",
    "reports/executive_summary.md",
    "reports/03_woe_iv_variable_summary.csv",
    "reports/05_score_band_summary.csv",
    "reports/06_validation_metrics.csv",
    "reports/08_cutoff_strategy.csv",
    "reports/09_expected_loss_by_risk_grade.csv",
    "reports/10_monitoring_psi.csv",
    "reports/11_reject_inference_sensitivity.csv",
    "reports/16_credit_lifecycle_map.csv",
    "reports/17_risk_taxonomy_matrix.csv",
    "reports/18_unexpected_loss_stress_buffer.csv",
    "reports/19_vintage_analysis.csv",
    "reports/20_roll_rate_framework_matrix.csv",
    "reports/21_ifrs9_ecl_bridge.csv",
    "reports/22_stress_testing_scenarios.csv",
    "reports/23_risk_based_pricing_by_grade.csv",
    "reports/24_collections_recovery_strategy.csv",
    "reports/25_concentration_risk_by_segment.csv",
    "reports/26_model_monitoring_triggers.csv",
    "reports/27_override_policy_simulation.csv",
    "reports/28_project_scope_completion_status.csv",
    "reports/29_formula_test_cases.csv",
    "reports/30_project3_completion_summary.md",
    "reports/31_financial_modeling_kpi_summary.csv",
    "reports/31_financial_modeling_numbers_and_conclusions.md",
    "reports/34_sample_quick_review.md",
    "reports/34_sample_quick_review_summary.json",
    "reports/34_sample_quick_review_by_grade.csv",
    "reports/34_sample_quick_review_by_decile.csv",
    "reports/35_enriched_feature_woe_detail.csv",
    "reports/35_enriched_feature_iv_summary.csv",
    "reports/35_enriched_formula_selected_features.csv",
    "reports/36_challenger_model_comparison.csv",
    "reports/36_challenger_model_summary.md",
    "reports/36_challenger_model_summary.json",
    "reports/36_challenger_acceptance_criteria.csv",
    "reports/36_expanded_scorecard_decile_pd.csv",
    "reports/37_population_bridge.csv",
    "reports/37_term_sensitivity_comparison.csv",
    "reports/37_enriched_split_drift_summary.csv",
    "reports/37_logistic_calibration_by_decile.csv",
    "reports/37_enriched_feature_csi_top5.csv",
    "reports/37_enriched_score_distribution_shift.csv",
    "reports/37_enriched_score_distribution_psi.csv",
    "reports/37_enriched_binning_quality_check.csv",
    "reports/37_feature_selection_rationale.csv",
    "reports/38_formula_scorecard_calibration_by_decile.csv",
    "reports/38_formula_vs_logistic_calibration_comparison.csv",
    "reports/38_formula_vs_woe_logistic_vs_raw_logistic_calibration.csv",
    "reports/38_tail_calibration_review.csv",
    "reports/38_binning_coarse_adjustment_log.csv",
    "reports/38_enriched_feature_iv_after_coarse_binning.csv",
    "reports/38_model_performance_after_coarse_binning.csv",
    "reports/38_feature_selection_governance.csv",
    "reports/38_feature_correlation_matrix.csv",
    "reports/38_redundant_feature_review.csv",
    "reports/38_woe_monotonicity_review.csv",
    "reports/38_woe_stability_train_test.csv",
    "reports/38_enriched_cutoff_strategy_formula_vs_logistic.csv",
    "reports/38_challenger_decision_matrix.csv",
    "reports/38_reject_inference_scope.csv",
    "reports/38_enriched_monitoring_triggers.csv",
    "reports/38_reason_code_mapping.csv",
    "reports/38_fairness_proxy_review.csv",
    "reports/38_governance_signoff_matrix.csv",
    "reports/39_woe_logistic_calibration_by_decile.csv",
    "reports/39_tail_recalibration_plan.csv",
    "reports/39_recalibrated_pd_by_decile.csv",
    "reports/39_woe_stability_after_coarse_binning.csv",
    "reports/39_final_scorecard_feature_governance_list.csv",
    "reports/40_final_clean_woe_logistic_scorecard_coefficients.csv",
    "reports/40_final_clean_woe_logistic_scorecard_points.csv",
    "reports/40_final_clean_woe_logistic_coefficient_sign_review.csv",
    "reports/40_benchmark_woe_logistic_scorecard_coefficients.csv",
    "reports/40_benchmark_woe_logistic_scorecard_points.csv",
    "reports/40_benchmark_woe_logistic_coefficient_sign_review.csv",
    "reports/40_final_clean_scorecard_exclusion_log.csv",
    "reports/40_recalibration_before_after_metrics.csv",
    "reports/40_post_coarse_model_stack_performance.csv",
    "reports/40_mort_acc_sensitivity.csv",
    "reports/40_final_model_recommendation.csv",
    "docs/methodology_note.md",
    "docs/formula_dictionary.md",
    "docs/model_card.md",
    "docs/validation_checklist.md",
    "docs/governance_and_limitations.md",
    "docs/interview_story.md",
    "docs/plan_traceability_matrix.md",
    "docs/advanced_framework_extensions.md",
    "docs/credit_lifecycle_map.md",
    "docs/risk_taxonomy_map.md",
    "docs/final_recruiter_interview_pack.md",
    "docs/risk_committee_memo.md",
    "excel/Credit_Risk_Formula_Engine.xlsx",
    "github/github_upload_checklist.md",
    "github/repo_description.md",
    "github/release_notes_v1.md",
    "github/publish_steps.md",
    "github/repo_file_manifest.csv",
    "powerbi/data_model.md",
    "powerbi/dax_measures.md",
    "powerbi/page_layout_spec.md",
    "powerbi/visual_mapping.csv",
    "powerbi/build_steps.md",
    "powerbi/theme.json",
    "sql/SQL_Risk_KPI_Queries.sql",
    "website/web_case_study_copy.md",
    "visuals/observed_default_by_risk_grade.png",
    "visuals/cutoff_tradeoff.png",
    "visuals/expected_loss_by_risk_grade.png",
    "visuals/psi_monitoring.png",
    "visuals/vintage_default_rate.png",
    "visuals/stress_el_by_scenario.png",
    "visuals/concentration_el_top_segments.png",
    "visuals/challenger_auc_ks_comparison.png",
    "visuals/expanded_scorecard_decile_pd.png",
    "visuals/logistic_calibration_curve.png",
    "visuals/enriched_score_distribution_shift.png",
    "visuals/formula_vs_logistic_calibration_gap.png",
    "visuals/recalibration_before_after.png",
]


def assert_file(path: Path) -> dict[str, str | int]:
    if not path.exists():
        raise AssertionError(f"Missing required file: {path}")
    if path.is_file() and path.stat().st_size == 0:
        raise AssertionError(f"Empty required file: {path}")
    return {"file": path.relative_to(PROJECT).as_posix(), "size_bytes": path.stat().st_size}


def validate_metrics() -> dict[str, float | int]:
    summary = json.loads((PROJECT / "reports" / "formula_engine_summary.json").read_text(encoding="utf-8"))
    checks = {
        "account_rows": int(summary["account_rows"]),
        "matured_rows": int(summary["matured_rows"]),
        "matured_default_rate": float(summary["matured_default_rate"]),
        "test_auc": float(summary["test_auc"]),
        "test_ks": float(summary["test_ks"]),
        "test_brier": float(summary["test_brier"]),
        "reject_population_rows": int(summary["reject_population_rows"]),
    }
    assert checks["account_rows"] >= 1_000_000
    assert checks["matured_rows"] >= 1_000_000
    assert 0 < checks["matured_default_rate"] < 1
    assert checks["test_auc"] >= 0.60
    assert checks["test_ks"] >= 0.15
    assert checks["test_brier"] < 0.25
    assert checks["reject_population_rows"] >= 20_000_000
    return checks


def validate_tables() -> dict[str, int]:
    tables = {
        "woe_iv_rows": PROJECT / "reports" / "03_woe_iv_variable_summary.csv",
        "score_band_rows": PROJECT / "reports" / "05_score_band_summary.csv",
        "validation_rows": PROJECT / "reports" / "06_validation_metrics.csv",
        "cutoff_rows": PROJECT / "reports" / "08_cutoff_strategy.csv",
        "monitoring_rows": PROJECT / "reports" / "10_monitoring_psi.csv",
        "reject_rows": PROJECT / "reports" / "11_reject_inference_sensitivity.csv",
        "vintage_rows": PROJECT / "reports" / "19_vintage_analysis.csv",
        "stress_rows": PROJECT / "reports" / "22_stress_testing_scenarios.csv",
        "pricing_rows": PROJECT / "reports" / "23_risk_based_pricing_by_grade.csv",
        "concentration_rows": PROJECT / "reports" / "25_concentration_risk_by_segment.csv",
        "override_rows": PROJECT / "reports" / "27_override_policy_simulation.csv",
        "acceptance_rows": PROJECT / "reports" / "28_project_scope_completion_status.csv",
        "test_case_rows": PROJECT / "reports" / "29_formula_test_cases.csv",
        "financial_modeling_kpi_rows": PROJECT / "reports" / "31_financial_modeling_kpi_summary.csv",
        "sample_quick_review_grade_rows": PROJECT / "reports" / "34_sample_quick_review_by_grade.csv",
        "sample_quick_review_decile_rows": PROJECT / "reports" / "34_sample_quick_review_by_decile.csv",
        "enriched_feature_iv_rows": PROJECT / "reports" / "35_enriched_feature_iv_summary.csv",
        "enriched_selected_feature_rows": PROJECT / "reports" / "35_enriched_formula_selected_features.csv",
        "challenger_comparison_rows": PROJECT / "reports" / "36_challenger_model_comparison.csv",
        "challenger_acceptance_rows": PROJECT / "reports" / "36_challenger_acceptance_criteria.csv",
        "expanded_scorecard_decile_rows": PROJECT / "reports" / "36_expanded_scorecard_decile_pd.csv",
        "population_bridge_rows": PROJECT / "reports" / "37_population_bridge.csv",
        "term_sensitivity_rows": PROJECT / "reports" / "37_term_sensitivity_comparison.csv",
        "enriched_split_drift_rows": PROJECT / "reports" / "37_enriched_split_drift_summary.csv",
        "logistic_calibration_rows": PROJECT / "reports" / "37_logistic_calibration_by_decile.csv",
        "enriched_feature_csi_rows": PROJECT / "reports" / "37_enriched_feature_csi_top5.csv",
        "score_distribution_shift_rows": PROJECT / "reports" / "37_enriched_score_distribution_shift.csv",
        "binning_quality_rows": PROJECT / "reports" / "37_enriched_binning_quality_check.csv",
        "feature_selection_rationale_rows": PROJECT / "reports" / "37_feature_selection_rationale.csv",
        "tail_calibration_rows": PROJECT / "reports" / "38_tail_calibration_review.csv",
        "coarse_binning_log_rows": PROJECT / "reports" / "38_binning_coarse_adjustment_log.csv",
        "coarse_performance_rows": PROJECT / "reports" / "38_model_performance_after_coarse_binning.csv",
        "three_model_calibration_rows": PROJECT / "reports" / "38_formula_vs_woe_logistic_vs_raw_logistic_calibration.csv",
        "feature_selection_governance_rows": PROJECT / "reports" / "38_feature_selection_governance.csv",
        "challenger_decision_rows": PROJECT / "reports" / "38_challenger_decision_matrix.csv",
        "reason_code_rows": PROJECT / "reports" / "38_reason_code_mapping.csv",
        "fairness_proxy_rows": PROJECT / "reports" / "38_fairness_proxy_review.csv",
        "governance_signoff_rows": PROJECT / "reports" / "38_governance_signoff_matrix.csv",
        "woe_logistic_calibration_rows": PROJECT / "reports" / "39_woe_logistic_calibration_by_decile.csv",
        "tail_recalibration_plan_rows": PROJECT / "reports" / "39_tail_recalibration_plan.csv",
        "recalibrated_pd_rows": PROJECT / "reports" / "39_recalibrated_pd_by_decile.csv",
        "post_coarse_woe_stability_rows": PROJECT / "reports" / "39_woe_stability_after_coarse_binning.csv",
        "feature_governance_list_rows": PROJECT / "reports" / "39_final_scorecard_feature_governance_list.csv",
        "final_clean_coefficients_rows": PROJECT / "reports" / "40_final_clean_woe_logistic_scorecard_coefficients.csv",
        "final_clean_points_rows": PROJECT / "reports" / "40_final_clean_woe_logistic_scorecard_points.csv",
        "final_clean_sign_review_rows": PROJECT / "reports" / "40_final_clean_woe_logistic_coefficient_sign_review.csv",
        "benchmark_sign_review_rows": PROJECT / "reports" / "40_benchmark_woe_logistic_coefficient_sign_review.csv",
        "clean_exclusion_rows": PROJECT / "reports" / "40_final_clean_scorecard_exclusion_log.csv",
        "recalibration_before_after_rows": PROJECT / "reports" / "40_recalibration_before_after_metrics.csv",
        "post_coarse_stack_rows": PROJECT / "reports" / "40_post_coarse_model_stack_performance.csv",
        "mort_acc_sensitivity_rows": PROJECT / "reports" / "40_mort_acc_sensitivity.csv",
        "final_recommendation_rows": PROJECT / "reports" / "40_final_model_recommendation.csv",
    }
    out = {}
    for key, path in tables.items():
        frame = pd.read_csv(path)
        assert len(frame) > 0, path
        out[key] = len(frame)
    challenger = pd.read_csv(PROJECT / "reports" / "36_challenger_model_comparison.csv")
    formula_test = challenger[
        challenger["sample"].eq("test_2017") & challenger["model_name"].eq("Expanded WOE formula scorecard")
    ].iloc[0]
    logistic_test = challenger[
        challenger["sample"].eq("test_2017") & challenger["model_name"].eq("Logistic regression challenger")
    ].iloc[0]
    assert float(formula_test["auc"]) >= 0.74
    assert float(formula_test["ks"]) >= 0.35
    assert float(logistic_test["auc"]) >= float(formula_test["auc"])
    assert float(logistic_test["ks"]) >= float(formula_test["ks"])
    woe_logit = challenger[
        challenger["sample"].eq("test_2017") & challenger["model_name"].eq("WOE logistic scorecard")
    ].iloc[0]
    assert float(woe_logit["auc"]) >= float(formula_test["auc"])
    term = pd.read_csv(PROJECT / "reports" / "37_term_sensitivity_comparison.csv")
    assert {"Expanded WOE without term", "Logistic without term"}.issubset(set(term["model_name"]))
    calibration = pd.read_csv(PROJECT / "reports" / "37_logistic_calibration_by_decile.csv")
    assert calibration["logistic_calibration_decile"].nunique() == 10
    tail = pd.read_csv(PROJECT / "reports" / "38_tail_calibration_review.csv")
    assert tail["action"].str.contains("Recalibrate").any()
    coarse = pd.read_csv(PROJECT / "reports" / "38_enriched_feature_iv_after_coarse_binning.csv")
    assert coarse["minimum_count_rule_status"].eq("Pass").all()
    points = pd.read_csv(PROJECT / "reports" / "40_final_clean_woe_logistic_scorecard_points.csv")
    legacy_sparse_pairs = {
        ("dti_band_exp", "40-60"),
        ("dti_band_exp", "60+"),
        ("purpose_exp", "educational"),
        ("purpose_exp", "wedding"),
        ("purpose_exp", "renewable_energy"),
        ("purpose_exp", "house"),
    }
    actual_pairs = set(zip(points["feature"].astype(str), points["bin"].astype(str)))
    assert not actual_pairs.intersection(legacy_sparse_pairs)
    assert "revol_util_band_exp" not in set(points["feature"].astype(str))
    assert "mort_acc_band_exp" not in set(points["feature"].astype(str))
    assert "bankruptcy_band_exp" not in set(points["feature"].astype(str))
    sign_review = pd.read_csv(PROJECT / "reports" / "40_final_clean_woe_logistic_coefficient_sign_review.csv")
    assert {"expected_sign", "actual_sign", "status", "action"}.issubset(sign_review.columns)
    assert not sign_review["status"].eq("Review").any()
    benchmark_sign = pd.read_csv(PROJECT / "reports" / "40_benchmark_woe_logistic_coefficient_sign_review.csv")
    assert benchmark_sign.loc[benchmark_sign["feature"].eq("revol_util_band_exp"), "status"].iloc[0] == "Review"
    clean_exclusion = pd.read_csv(PROJECT / "reports" / "40_final_clean_scorecard_exclusion_log.csv")
    assert {"revol_util_band_exp", "mort_acc_band_exp", "bankruptcy_band_exp"}.issubset(set(clean_exclusion["feature"]))
    acceptance = pd.read_csv(PROJECT / "reports" / "36_challenger_acceptance_criteria.csv")
    calibration_status = acceptance.loc[acceptance["criterion"].eq("Calibration discipline"), "status"].iloc[0]
    assert calibration_status in {"Conditional Pass", "Pass for portfolio benchmark; production control required"}
    recalibrated = pd.read_csv(PROJECT / "reports" / "39_recalibrated_pd_by_decile.csv")
    assert "evaluation_use" in recalibrated.columns
    test_decile_10 = recalibrated[(recalibrated["sample"].eq("test_2017")) & (recalibrated["decile"].eq(10))].iloc[0]
    assert abs(float(test_decile_10["post_recalibration_gap"])) <= abs(float(test_decile_10["pre_recalibration_gap"]))
    recal_metrics = pd.read_csv(PROJECT / "reports" / "40_recalibration_before_after_metrics.csv")
    assert {"mean_abs_calibration_gap_before", "mean_abs_calibration_gap_after", "brier_score_before", "brier_score_after", "decision"}.issubset(recal_metrics.columns)
    final_features = pd.read_csv(PROJECT / "reports" / "39_final_scorecard_feature_governance_list.csv")
    assert "woe_stability_threshold_rule" in final_features.columns
    excluded_final_flags = final_features.loc[
        final_features["feature"].isin(["revol_util_band_exp", "mort_acc_band_exp", "bankruptcy_band_exp"]),
        "selected_for_final_clean_scorecard",
    ].astype(str).str.lower()
    assert not excluded_final_flags.eq("true").any()
    stack = pd.read_csv(PROJECT / "reports" / "40_post_coarse_model_stack_performance.csv")
    assert {"Coarse expanded WOE formula", "Final clean WOE-logistic scorecard", "Raw logistic challenger"}.issubset(set(stack["model"]))
    recommendation = pd.read_csv(PROJECT / "reports" / "40_final_model_recommendation.csv")
    assert "Final clean WOE-logistic scorecard" in set(recommendation["model"])
    three_model = pd.read_csv(PROJECT / "reports" / "38_formula_vs_woe_logistic_vs_raw_logistic_calibration.csv")
    assert {"formula_gap", "woe_logistic_gap", "raw_logistic_gap"}.issubset(three_model.columns)
    out["expanded_formula_test_auc"] = float(formula_test["auc"])
    out["woe_logistic_test_auc"] = float(woe_logit["auc"])
    out["logistic_challenger_test_auc"] = float(logistic_test["auc"])
    return out


def validate_completion_pack() -> dict[str, str | int | float]:
    completion = json.loads((PROJECT / "reports" / "completion_pack_summary.json").read_text(encoding="utf-8"))
    tests = pd.read_csv(PROJECT / "reports" / "29_formula_test_cases.csv")
    acceptance = pd.read_csv(PROJECT / "reports" / "28_project_scope_completion_status.csv")
    stress = pd.read_csv(PROJECT / "reports" / "22_stress_testing_scenarios.csv")
    pricing = pd.read_csv(PROJECT / "reports" / "23_risk_based_pricing_by_grade.csv")

    assert completion["status"] == "complete"
    assert int(completion["formula_tests_passed"]) == int(completion["formula_tests_total"]) == len(tests)
    assert tests["status"].eq("PASS").all()
    assert len(acceptance) >= 20
    assert {"Base", "Mild Downturn", "Adverse", "Severe"}.issubset(set(stress["scenario"]))
    assert pricing["required_rate"].between(0, 1).all()

    workbook = PROJECT / "excel" / "Credit_Risk_Formula_Engine.xlsx"
    assert workbook.exists() and workbook.stat().st_size > 50_000
    return {
        "completion_status": completion["status"],
        "formula_tests_passed": int(completion["formula_tests_passed"]),
        "formula_tests_total": int(completion["formula_tests_total"]),
        "acceptance_items": len(acceptance),
        "excel_workbook_size_bytes": workbook.stat().st_size,
        "severe_stressed_el": float(stress.loc[stress["scenario"].eq("Severe"), "stressed_el"].sum()),
        "max_required_rate": float(pricing["required_rate"].max()),
    }


def validate_public_surfaces() -> dict[str, str]:
    readme_path = PROJECT / "README.md"
    index_path = PROJECT / "index.html"
    web_copy_path = PROJECT / "website" / "web_case_study_copy.md"
    data_access_path = PROJECT / "DATA_ACCESS.md"
    governance_path = PROJECT / "docs" / "governance_and_limitations.md"
    for path in [readme_path, index_path, web_copy_path, data_access_path, governance_path]:
        assert path.exists(), path

    public_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [readme_path, index_path, web_copy_path, data_access_path, governance_path]
    )
    required = [
        "Credit Risk Scorecard & Portfolio Analytics",
        "0.626",
        "0.180",
        "0.765",
        "0.793",
        "49.47%",
        "64.07%",
        "03_CreditRiskDecisionEngine",
        "End-to-end credit risk management",
        "Excel Workbook",
        "15 / 15",
        "Financial modeling numbers",
        "19.42B",
        "511.29M",
        "28.13%",
        "moderate ranking power",
        "expanded WOE formula scorecard",
        "Final clean WOE-logistic scorecard",
        "logistic regression challenger",
        "Population Bridge",
        "not directly comparable",
        "Term sensitivity",
        "High-risk tail calibration",
        "accepted/booked accounts",
        "Positioning Note",
        "not a production automated underwriting model",
        "Primary data source",
        "LendingClub accepted loan data + rejected applicant data",
        "Author local path example",
        "Portable repo path",
        "Light Rebuild Mode",
        "EAD consistency note",
        "EL consistency note",
        "Illustrative risk appetite",
        "Formula PD",
        "mechanically mapped from observed default rates",
        "+3.50 pp",
        "Monitoring Triggers",
        "Limitation | Impact | Mitigation",
        "Governance Ownership",
        "In one minute:",
        "With internal bank data, I would improve",
        "Fairness / Proxy Review",
        "Challenger Model Note",
        "Challenger acceptance criteria",
        "home_ownership",
        "income_missing",
        "Improve AUC/KS materially",
        "Reviewer quick-run without Project 0",
        "python scripts/06_quick_review_from_sample.py",
        "100k sample",
        "Project folder has an index page",
    ]
    forbidden = [
        "02_PDModeling",
        "0.674",
        "0.250",
        "65.1%",
        "53.2%",
        "Current draft",
        "Protect approval volume",
        "Preserve good volume",
        "The model shows exposure",
        "The model is useful because",
        "Layer " + "1 engine",
        ">Project " + "Folder<",
    ]
    missing = [item for item in required if item not in public_text]
    stale = [item for item in forbidden if item in public_text]
    assert not missing, f"Public surfaces missing: {missing}"
    assert not stale, f"Public surfaces stale content: {stale}"
    return {
        "readme": readme_path.relative_to(PROJECT).as_posix(),
        "project_index": index_path.relative_to(PROJECT).as_posix(),
        "website_copy": web_copy_path.relative_to(PROJECT).as_posix(),
        "data_access": data_access_path.relative_to(PROJECT).as_posix(),
    }


def validate_docs() -> dict[str, str]:
    doc_checks = {
        "reject inference sensitivity": PROJECT / "docs" / "advanced_framework_extensions.md",
        "WOE smoothing": PROJECT / "docs" / "advanced_framework_extensions.md",
        "Behavioral CCF applies only": PROJECT / "docs" / "advanced_framework_extensions.md",
        "SICR": PROJECT / "docs" / "advanced_framework_extensions.md",
        "Contingency modes": PROJECT / "docs" / "advanced_framework_extensions.md",
        "Layer 15": PROJECT / "docs" / "plan_traceability_matrix.md",
        "Credit Lifecycle Map": PROJECT / "docs" / "credit_lifecycle_map.md",
        "Credit Risk Taxonomy Map": PROJECT / "docs" / "risk_taxonomy_map.md",
        "CV bullet": PROJECT / "docs" / "final_recruiter_interview_pack.md",
        "Financial Modeling Numbers And Conclusions": PROJECT / "reports" / "31_financial_modeling_numbers_and_conclusions.md",
        "approved EAD": PROJECT / "reports" / "31_financial_modeling_numbers_and_conclusions.md",
        "Required pricing": PROJECT / "reports" / "31_financial_modeling_numbers_and_conclusions.md",
        "moderate ranking power": PROJECT / "README.md",
        "+3.50 pp": PROJECT / "README.md",
        "full raw data is not committed": PROJECT / "README.md",
        "Public Data Sources": PROJECT / "DATA_ACCESS.md",
        "Positioning Note": PROJECT / "README.md",
        "UCI Default of Credit Card Clients is methodology reference only": PROJECT / "README.md",
        "EAD consistency note": PROJECT / "README.md",
        "Governance And Next Improvements": PROJECT / "README.md",
        "Reviewer quick-run without Project 0": PROJECT / "README.md",
        "Light Rebuild Mode": PROJECT / "DATA_ACCESS.md",
        "Sample Quick Review": PROJECT / "reports" / "34_sample_quick_review.md",
        "Limitation | Impact | Mitigation": PROJECT / "docs" / "governance_and_limitations.md",
        "Governance Ownership": PROJECT / "docs" / "governance_and_limitations.md",
        "Fairness / Proxy Review": PROJECT / "docs" / "governance_and_limitations.md",
        "Proxy / fairness concern": PROJECT / "docs" / "governance_and_limitations.md",
        "Challenger Model Note": PROJECT / "docs" / "governance_and_limitations.md",
        "Challenger acceptance criteria": PROJECT / "docs" / "governance_and_limitations.md",
        "formula-first risk engine": PROJECT / "reports" / "31_financial_modeling_numbers_and_conclusions.md",
        "Enriched Scorecard And Challenger Benchmark": PROJECT / "reports" / "36_challenger_model_summary.md",
        "Population Bridge": PROJECT / "reports" / "36_challenger_model_summary.md",
        "Term Sensitivity": PROJECT / "reports" / "36_challenger_model_summary.md",
        "Enriched Split Drift": PROJECT / "reports" / "36_challenger_model_summary.md",
        "Classic Scorecard Caveat": PROJECT / "reports" / "36_challenger_model_summary.md",
        "High-Risk Tail Calibration": PROJECT / "reports" / "36_challenger_model_summary.md",
        "Logistic regression challenger": PROJECT / "reports" / "36_challenger_model_summary.md",
        "37_logistic_calibration_by_decile.csv": PROJECT / "docs" / "model_card.md",
        "40_final_clean_woe_logistic_scorecard_points.csv": PROJECT / "docs" / "model_card.md",
        "Risk Committee Memo": PROJECT / "docs" / "risk_committee_memo.md",
        "not directly comparable": PROJECT / "docs" / "model_card.md",
        "FINANCIAL_RISK_DATA_CORE": PROJECT / "DATA_ACCESS.md",
        "The full raw data is intentionally not committed": PROJECT / "DATA_ACCESS.md",
        "git push -u origin main": PROJECT / "github" / "publish_steps.md",
    }
    for phrase, path in doc_checks.items():
        text = path.read_text(encoding="utf-8")
        assert phrase in text, f"Missing phrase {phrase!r} in {path}"
    return {"docs": "advanced framework and traceability docs validated"}


def main() -> None:
    forbidden_legacy_reports = [
        "reports/38_" + "woe_logistic_scorecard_coefficients.csv",
        "reports/38_" + "woe_logistic_scorecard_points.csv",
        "reports/38_" + "woe_logistic_coefficient_sign_review.csv",
        "reports/39_final_" + "production_candidate_feature_list.csv",
        "reports/28_" + "acceptance_criteria_status.csv",
    ]
    legacy_present = [rel for rel in forbidden_legacy_reports if (PROJECT / rel).exists()]
    assert not legacy_present, f"Legacy confusing reports still present: {legacy_present}"

    file_results = [assert_file(PROJECT / rel) for rel in REQUIRED_FILES]
    metric_results = validate_metrics()
    table_results = validate_tables()
    completion_results = validate_completion_pack()
    public_surface_results = validate_public_surfaces()
    doc_results = validate_docs()

    audit = {
        "status": "pass",
        "required_files": len(file_results),
        "metrics": metric_results,
        "tables": table_results,
        "completion_pack": completion_results,
        "public_surfaces": public_surface_results,
        "docs": doc_results,
    }
    (PROJECT / "reports" / "validation_audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    markdown = ["# Validation Audit", "", "Status: **PASS**", "", "## Metrics"]
    for key, value in metric_results.items():
        markdown.append(f"- `{key}`: {value}")
    markdown.extend(["", "## Tables"])
    for key, value in table_results.items():
        markdown.append(f"- `{key}`: {value}")
    markdown.extend(["", "## Completion Pack"])
    for key, value in completion_results.items():
        markdown.append(f"- `{key}`: {value}")
    markdown.extend(["", f"Required files checked: {len(file_results)}"])
    (PROJECT / "reports" / "validation_audit.md").write_text("\n".join(markdown), encoding="utf-8")
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
