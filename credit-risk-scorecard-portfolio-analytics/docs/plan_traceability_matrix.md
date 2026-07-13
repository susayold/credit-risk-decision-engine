# Project 3 Plan Traceability Matrix

This matrix tracks the build against the approved Project 3 plan. Status meanings:

- **Done**: implemented with data-backed outputs or documentation.
- **Partial**: implemented with limitation, proxy or framework treatment.
- **Pending**: not built yet.

## Layer Tracking

| Plan layer | Requirement | Status | Evidence | Remaining work |
|---|---|---|---|---|
| Layer 0 - Credit Risk Business Context | Explain lender, product, borrower, credit decision and loss source | Done | `README.md`, `reports/executive_summary.md`, `docs/interview_story.md`, `reports/30_project3_completion_summary.md` | Add public GitHub/web links after publishing |
| Layer 1 - Credit Lifecycle | Map application to monitoring lifecycle and risk questions | Done | `docs/credit_lifecycle_map.md`, `reports/16_credit_lifecycle_map.csv` | Monthly DPD servicing data remains unavailable |
| Layer 2 - Population, Data & Target Definition | Application, booked, matured, rejected, good/bad/indeterminate, leakage and reject inference | Done | Project 0 data readiness files, `reports/01_population_target_summary.csv`, `reports/11_reject_inference_sensitivity.csv`, `docs/model_card.md` | Reject outcomes remain unobserved by design |
| Layer 3 - Credit Risk Taxonomy | Connect risk types to formulas, metrics and decisions | Done | `docs/risk_taxonomy_map.md`, `reports/17_risk_taxonomy_matrix.csv` | None for portfolio scope |
| Layer 4 - Core Credit Risk Formula Engine | Default rate, PD, LGD, EAD, EL, unexpected loss, recovery, delinquency | Done | `scripts/01_build_formula_first_engine.py`, `scripts/03_build_completion_pack.py`, `reports/02_formula_dictionary.csv`, `reports/09_expected_loss_by_risk_grade.csv`, `reports/18_unexpected_loss_stress_buffer.csv` | True recovery cashflows and DPD delinquency require internal servicing data |
| Layer 5 - Risk Drivers, Binning, WOE & IV | Binning, WOE, IV, smoothing, missing/outlier handling | Done | `reports/03_woe_iv_variable_summary.csv`, Project 0 WOE ready table, `docs/methodology_note.md` | Add detailed bin table export later if needed |
| Layer 6 - Scorecard & Risk Segmentation | Good odds, scorecard points, score bands and risk grade mapping | Done | `reports/04_decile_pd_mapping.csv`, `reports/05_score_band_summary.csv`, `reports/40_final_clean_woe_logistic_scorecard_points.csv`, `docs/formula_dictionary.md` | Future work: production-grade scorecard refit with internal bank data |
| Layer 7 - Credit Policy & Decision Engine | Approve/review/decline, limit/pricing control, override policy | Done | `reports/08_cutoff_strategy.csv`, `reports/27_override_policy_simulation.csv`, `docs/governance_and_limitations.md` | True override records are unavailable; override output is simulation/framework |
| Layer 8 - Validation, Calibration & Model Performance | AUC, Gini, KS, Brier, calibration and backtesting | Done | `reports/06_validation_metrics.csv`, `reports/07_calibration_by_decile.csv`, `reports/36_challenger_model_comparison.csv`, `reports/38_formula_vs_woe_logistic_vs_raw_logistic_calibration.csv`, `reports/40_recalibration_before_after_metrics.csv`, `reports/40_post_coarse_model_stack_performance.csv`, `docs/validation_checklist.md` | Challenger model implemented: expanded WOE formula, final clean WOE-logistic scorecard and raw logistic regression. Future work: calibrated gradient boosting / external validation. |
| Layer 9 - Portfolio Risk Monitoring | PSI, vintage, roll-rate, early warning and model degradation | Done | `reports/10_monitoring_psi.csv`, `reports/19_vintage_analysis.csv`, `reports/20_roll_rate_framework_matrix.csv`, `reports/26_model_monitoring_triggers.csv` | True roll-rate requires monthly DPD history; framework is documented |
| Layer 10 - IFRS 9 ECL & Provisioning Bridge | Stage 1/2/3, SICR, 12-month/lifetime ECL, forward-looking adjustment | Done | `reports/21_ifrs9_ecl_bridge.csv`, `docs/advanced_framework_extensions.md` | Bridge only; Project 4 can build full audited-style ECL engine |
| Layer 11 - Stress Testing & Scenario Analysis | Base/adverse/severe PD/LGD/EAD shock and macro overlay | Done | `reports/22_stress_testing_scenarios.csv`, `reports/18_unexpected_loss_stress_buffer.csv`, `visuals/stress_el_by_scenario.png` | Scenario relationship is illustrative |
| Layer 12 - Risk-Based Pricing & Profitability | Risk-adjusted profit, required rate and RAROC | Done | `reports/23_risk_based_pricing_by_grade.csv` | Funding, operating, capital cost and economic capital remain assumptions |
| Layer 13 - Collections & Recovery Strategy | Collection metrics, cure, roll-back, write-off and recovery framework | Done | `reports/24_collections_recovery_strategy.csv`, `reports/15_sba_chargeoff_reference_profile.csv` | Consumer collection actions and recovery cashflows unavailable |
| Layer 14 - Concentration Risk | Exposure share, EL share and top segment concentration | Done | `reports/25_concentration_risk_by_segment.csv`, `visuals/concentration_el_top_segments.png`, Power BI spec | None for portfolio scope |
| Layer 15 - Model Risk, Governance & Documentation | Intended use, limitations, monitoring, recalibration and contingency | Done | `docs/model_card.md`, `docs/governance_and_limitations.md`, `docs/validation_checklist.md`, `github/github_upload_checklist.md` | Add independent review checklist later if needed |

## Current Build Priority

The current repo is at **end-to-end formula-first completion v1**:

1. Data-backed target, WOE/IV, scorecard, validation, cutoff and expected loss are implemented.
2. Lifecycle, taxonomy, vintage, ECL bridge, stress, pricing, collection, concentration, override and monitoring trigger artifacts are implemented.
3. Formula test cases pass 15/15.
4. Excel master workbook is generated.
5. Challenger model implemented: expanded WOE formula, WOE-logistic scorecard and raw logistic regression.
6. Coarse-binning, coefficient sign review, three-model calibration comparison and tail recalibration candidate artifacts are implemented.
7. Website packaging is being finalized.
