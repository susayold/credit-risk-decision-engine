# Artifact Index

## Core Engine

| Artifact | Purpose |
|---|---|
| `scripts/01_build_formula_first_engine.py` | Rebuilds Project 3 formula-first outputs |
| `scripts/02_validate_project3_outputs.py` | Validates required outputs before GitHub/web upload |
| `scripts/03_build_completion_pack.py` | Builds senior completion pack: monitoring, ECL, stress, pricing, Excel and tests |
| `scripts/04_build_financial_modeling_summary.py` | Builds finance-facing KPI and conclusions report |
| `scripts/06_quick_review_from_sample.py` | Runs reviewer quick-checks from the included 100k sample |
| `scripts/07_package_portable_zip.py` | Creates portable ZIP packages with forward-slash archive paths |
| `scripts/08_build_enriched_scorecard_challenger.py` | Builds enriched scorecard and logistic challenger benchmark |
| `reports/formula_engine_summary.json` | Machine-readable headline metrics |
| `reports/completion_pack_summary.json` | Machine-readable completion-pack metrics |
| `data/processed/formula_engine_account_sample.csv.gz` | 100k account-level sample for inspection/demo |
| `data/processed/enriched_scorecard_challenger_sample.csv.gz` | 100k enriched modeling sample for inspection/demo |

## Reports

| Artifact | Purpose |
|---|---|
| `reports/01_population_target_summary.csv` | Population, maturity and expected loss summary |
| `reports/02_formula_dictionary.csv` | Formula catalog |
| `reports/03_woe_iv_variable_summary.csv` | WOE/IV driver strength |
| `reports/04_decile_pd_mapping.csv` | Decile-to-PD mapping |
| `reports/05_score_band_summary.csv` | Risk grade performance |
| `reports/06_validation_metrics.csv` | AUC, Gini, KS, Brier and calibration |
| `reports/07_calibration_by_decile.csv` | Decile calibration |
| `reports/08_cutoff_strategy.csv` | Approval/review cutoff trade-off |
| `reports/09_expected_loss_by_risk_grade.csv` | Expected loss by risk grade |
| `reports/10_monitoring_psi.csv` | Yearly PSI monitoring |
| `reports/11_reject_inference_sensitivity.csv` | Reject inference scenarios |
| `reports/12_data_gap_status.csv` | Data gaps and handling |
| `reports/13_module_coverage_status.csv` | Module support level |
| `reports/16_credit_lifecycle_map.csv` | Lifecycle-stage risk questions |
| `reports/17_risk_taxonomy_matrix.csv` | Risk type to formula/metric/decision map |
| `reports/18_unexpected_loss_stress_buffer.csv` | Unexpected loss and stress buffer by grade |
| `reports/19_vintage_analysis.csv` | Vintage bad-rate and EL monitoring |
| `reports/20_roll_rate_framework_matrix.csv` | Roll-rate matrix framework with data limitation |
| `reports/21_ifrs9_ecl_bridge.csv` | IFRS 9 Stage 1/2/3 ECL bridge |
| `reports/22_stress_testing_scenarios.csv` | Base/mild/adverse/severe scenario outputs |
| `reports/23_risk_based_pricing_by_grade.csv` | Required pricing and RAROC proxy |
| `reports/24_collections_recovery_strategy.csv` | Collections and recovery action matrix |
| `reports/25_concentration_risk_by_segment.csv` | EAD/EL concentration by segment |
| `reports/26_model_monitoring_triggers.csv` | Monitoring thresholds and management actions |
| `reports/27_override_policy_simulation.csv` | Override candidate simulation |
| `reports/28_project_scope_completion_status.csv` | Project scope completion status |
| `reports/29_formula_test_cases.csv` | Formula test cases and pass/fail evidence |
| `reports/30_project3_completion_summary.md` | Final project completion summary |
| `reports/31_financial_modeling_kpi_summary.csv` | Finance-facing KPI summary |
| `reports/31_financial_modeling_numbers_and_conclusions.md` | Full financial modeling numbers and management conclusions |
| `reports/34_sample_quick_review.md` | Lightweight sample review for recruiters without Project 0 |
| `reports/34_sample_quick_review_summary.json` | Machine-readable quick-review sample metrics |
| `reports/34_sample_quick_review_by_grade.csv` | Sample risk-grade summary |
| `reports/34_sample_quick_review_by_decile.csv` | Sample risk-decile summary |
| `reports/35_enriched_feature_woe_detail.csv` | WOE detail for enriched scorecard variables |
| `reports/35_enriched_feature_iv_summary.csv` | Enriched feature IV ranking and selected-feature flag |
| `reports/35_enriched_formula_selected_features.csv` | Features selected into expanded WOE formula scorecard |
| `reports/36_challenger_model_comparison.csv` | Formula scorecard vs logistic challenger metrics |
| `reports/36_challenger_model_summary.md` | Senior interpretation of enriched scorecard/challenger results |
| `reports/36_challenger_acceptance_criteria.csv` | Challenger acceptance criteria and status |
| `reports/36_expanded_scorecard_decile_pd.csv` | Expanded scorecard decile PD map |
| `reports/37_population_bridge.csv` | Clarifies 1.3M portfolio base vs 331.9K enriched sample vs rejected applicants |
| `reports/37_term_sensitivity_comparison.csv` | With-term vs without-term sensitivity for formula and logistic models |
| `reports/37_enriched_split_drift_summary.csv` | Train/validation/test default and average PD drift |
| `reports/37_logistic_calibration_by_decile.csv` | Logistic challenger calibration by decile |
| `reports/37_enriched_feature_csi_top5.csv` | Top-feature CSI versus train window |
| `reports/37_enriched_score_distribution_shift.csv` | Expanded scorecard decile distribution shift |
| `reports/37_enriched_binning_quality_check.csv` | Pre-coarse sparse-bin diagnostic, not final production binning |
| `reports/37_feature_selection_rationale.csv` | Feature keep/drop rationale for the enriched benchmark |
| `reports/38_tail_calibration_review.csv` | High-risk decile 9-10 calibration review |
| `reports/38_formula_vs_woe_logistic_vs_raw_logistic_calibration.csv` | Three-model calibration comparison by test decile |
| `reports/38_binning_coarse_adjustment_log.csv` | Sparse-bin coarse-binning adjustment log |
| `reports/38_model_performance_after_coarse_binning.csv` | Performance after coarse-binning sparse bins |
| `reports/38_feature_selection_governance.csv` | Feature selection governance beyond IV threshold |
| `reports/38_feature_correlation_matrix.csv` | WOE-transformed feature correlation matrix |
| `reports/38_redundant_feature_review.csv` | Redundancy review for correlated feature pairs |
| `reports/38_woe_monotonicity_review.csv` | WOE monotonicity review |
| `reports/38_woe_stability_train_test.csv` | WOE stability across train/validation/test |
| `reports/38_enriched_cutoff_strategy_formula_vs_logistic.csv` | Enriched cutoff benchmark: formula vs WOE-logistic vs raw logistic |
| `reports/38_challenger_decision_matrix.csv` | Challenger decision matrix across performance and governance criteria |
| `reports/38_reason_code_mapping.csv` | Adverse-action style reason code mapping |
| `reports/38_fairness_proxy_review.csv` | Fairness/proxy variable review |
| `reports/38_governance_signoff_matrix.csv` | Required governance sign-off matrix |
| `reports/39_woe_logistic_calibration_by_decile.csv` | WOE-logistic calibration by decile |
| `reports/39_tail_recalibration_plan.csv` | Tail recalibration plan for high-risk deciles |
| `reports/39_recalibrated_pd_by_decile.csv` | Candidate validation-factor recalibrated PD by decile |
| `reports/39_woe_stability_after_coarse_binning.csv` | WOE stability after coarse-binning |
| `reports/39_final_scorecard_feature_governance_list.csv` | Final clean scorecard feature governance list with WOE-stability thresholds |
| `reports/40_final_clean_woe_logistic_scorecard_coefficients.csv` | Official final clean WOE-logistic scorecard coefficients |
| `reports/40_final_clean_woe_logistic_scorecard_points.csv` | Official final clean scorecard points |
| `reports/40_final_clean_woe_logistic_coefficient_sign_review.csv` | Official final clean coefficient sign review under WOE convention |
| `reports/40_benchmark_woe_logistic_scorecard_coefficients.csv` | Benchmark full post-coarse WOE-logistic coefficients before exclusion cleanup |
| `reports/40_benchmark_woe_logistic_scorecard_points.csv` | Benchmark full post-coarse WOE-logistic points before exclusion cleanup |
| `reports/40_benchmark_woe_logistic_coefficient_sign_review.csv` | Benchmark sign-review evidence showing why cleanup was needed |
| `reports/40_final_clean_scorecard_exclusion_log.csv` | Variables removed from final clean scorecard and governance reasons |
| `reports/40_recalibration_before_after_metrics.csv` | Recalibration before/after metrics and over-correction warning |
| `reports/40_post_coarse_model_stack_performance.csv` | Post-coarse performance for formula, clean WOE-logistic and raw logistic layers |
| `reports/40_mort_acc_sensitivity.csv` | WOE-logistic sensitivity with and without mortgage-account feature |
| `reports/40_final_model_recommendation.csv` | Final model use-case and status recommendation |
| `reports/executive_summary.md` | Business-facing summary |
| `reports/validation_audit.json` | Machine-readable validation audit |
| `reports/validation_audit.md` | Human-readable validation audit |

## Documentation

| Artifact | Purpose |
|---|---|
| `README.md` | GitHub front door |
| `docs/methodology_note.md` | Modeling methodology |
| `docs/formula_dictionary.md` | Credit risk formula definitions |
| `docs/model_card.md` | Governance model card |
| `docs/validation_checklist.md` | Validation evidence |
| `docs/governance_and_limitations.md` | Model risk and limitation control |
| `docs/interview_story.md` | Interview explanation |
| `docs/plan_traceability_matrix.md` | Plan layer tracking |
| `docs/advanced_framework_extensions.md` | Advanced risk framework modules |
| `docs/credit_lifecycle_map.md` | Lifecycle diagram and stage mapping |
| `docs/risk_taxonomy_map.md` | Credit risk taxonomy map |
| `docs/final_recruiter_interview_pack.md` | Recruiter pitch, CV bullet and interview story |
| `docs/risk_committee_memo.md` | One-page risk committee memo |

## Excel

| Artifact | Purpose |
|---|---|
| `excel/Credit_Risk_Formula_Engine.xlsx` | Excel master workbook with formula, validation, monitoring, ECL, stress, pricing and governance sheets |

## GitHub And Web

| Artifact | Purpose |
|---|---|
| `github/repo_description.md` | GitHub repo metadata |
| `github/github_upload_checklist.md` | Upload checklist |
| `website/web_case_study_copy.md` | Website copy |
| `powerbi/*` | Power BI-first dashboard pack |
| `sql/SQL_Risk_KPI_Queries.sql` | SQL KPI query examples |
