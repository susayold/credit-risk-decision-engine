# Project 3: Credit Risk Scorecard & Portfolio Analytics

Formula-first credit risk modeling for lending default risk.

This project builds a transparent credit risk scorecard and portfolio analytics workflow that turns borrower and loan data into risk bands, scorecard points, cutoff strategy and expected loss. It then extends the workflow into portfolio monitoring, IFRS 9 ECL bridge, stress testing, risk-based pricing, collections strategy, concentration risk and governance. It is designed for Risk Analyst, Risk Analytics, Credit Risk Modeling and Model Risk interview discussion.

## Positioning Note

This is a **formula-first credit risk analytics portfolio project**, not a production automated underwriting model. Data-backed modules include target definition, WOE/IV, PD bands, cutoff simulation, validation, PSI, vintage and concentration. Internal-bank modules such as workout LGD, override monitoring, collections effectiveness and full IFRS 9 ECL are documented as proxy/framework extensions due to public-data limitations.

In one minute: I built a formula-first credit risk scorecard and portfolio analytics project on lending data. It defines matured good/bad targets, builds WOE/IV risk drivers, maps score deciles to baseline PD, validates ranking and calibration, simulates cutoff policies, connects PD to expected loss, monitors portfolio drift and vintage behavior, and benchmarks the scorecard against a logistic regression challenger. The project is not a production underwriting model; it is a transparent portfolio-grade demonstration of credit risk analytics judgment.

## Business Problem

A lender needs to decide which lending accounts are low enough risk to approve, which accounts require review, and which accounts may create excessive expected loss. The project answers:

- Which accounts are likely to default?
- Which variables separate good and bad accounts?
- How strong is the formula score's ranking power?
- What cutoff balances approval volume and default risk?
- How much expected loss is created by each risk grade?
- What limitations should a risk team disclose?

## Data

Full raw data is excluded due to size. See `DATA_ACCESS.md` for public source links, local rebuild paths and full rebuild instructions.

Included portable sample paths:

`./data/processed/formula_engine_account_sample.csv.gz`

`./data/processed/enriched_scorecard_challenger_sample.csv.gz`

Primary data source:

- LendingClub accepted loan data + rejected applicant data.
- LendingClub accepted loan data.
- LendingClub rejected applicant data.
- UCI Default of Credit Card Clients is methodology reference only, not the primary data used in this project.

GitHub/recruiter note:

- The full raw data is not committed to the repo.
- The repo includes generated 100k samples for the portfolio baseline and enriched challenger layer.
- Full review can be done from the included sample, Excel workbook, aggregated reports, visuals and HTML case study.
- Full rebuild requires recreating the Project 0 data core from the public data sources listed in `DATA_ACCESS.md`.

Readiness snapshot:

| Metric | Value |
|---|---:|
| Account rows | 1,347,681 |
| Matured rows | 1,291,521 |
| Monitor-only rows | 56,160 |
| Matured default rate | 20.16% |
| Supplemental rejected applications | 27,648,741 |
| Supplemental enriched accepted rows | 331,865 |
| Supplemental SBA charge-off reference rows | 545,751 |

## Population Bridge

The project uses three related but distinct data layers. The AUC **0.626** baseline and the AUC **0.765 / 0.793** enriched models are **not directly comparable as the same model on the same population**.

| Dataset layer | Population | Rows | Features | Used for | Not used for |
|---|---|---:|---|---|---|
| Portfolio base | Accepted/booked lending accounts | 1,347,681 | Thin/core fields | Target, baseline PD, EL, cutoff, monitoring, stress/pricing framework | Enriched model benchmark |
| Enriched accepted sample | Accepted loans with richer application-time variables | 331,865 | 17 candidate features | Expanded WOE scorecard and logistic challenger | Direct comparison to 1.3M AUC as the same model/population |
| Rejected applicant data | Rejected applications | 27,648,741 | Application attributes only | Reject inference sensitivity and selection-bias discussion | Labeled reject model training; default outcomes are unobserved |

Interpretation: the baseline measures performance on the large portfolio foundation with a thinner feature set. The enriched models benchmark performance on a smaller accepted-loan sample with stronger application-time variables.

## Method

This is not ML-first. The core version is a formula-first scorecard workflow:

1. Define matured good/bad population.
2. Use WOE/IV to rank risk drivers.
3. Combine WOE values using IV-based weights.
4. Convert weighted WOE score into formula PD by score decile.
5. Convert PD into scorecard points using good-odds convention.
6. Map score bands to policy actions.
7. Validate ranking and calibration.
8. Simulate approval/review/decline cutoffs.
9. Connect PD to expected loss: `PD x LGD x EAD`.
10. Document limitations and monitoring controls.

Modeling hardening layer:

11. Use the enriched accepted-loan sample to add 17 candidate application-time risk features.
12. Fit enriched WOE/IV only on the 183,002-row training window, not on the full 331,865-row sample.
13. Benchmark the formula scorecard against a logistic regression challenger.
14. Keep the formula scorecard as the explanation layer and the logistic model as a performance benchmark.

The completion pack then adds:

15. Credit lifecycle and risk taxonomy maps.
16. Vintage analysis and roll-rate framework.
17. IFRS 9 ECL bridge and stress scenarios.
18. Risk-based pricing and RAROC proxy.
19. Collections/recovery strategy and override simulation.
20. Concentration risk and monitoring triggers.
21. Excel master workbook and formula test cases.

## Results

Three-layer performance summary:

| Layer | Population | Role | Test AUC | Test Gini | Test KS |
|---|---|---|---:|---:|---:|
| Thin baseline scorecard | 1.3M portfolio base | Target, EL, cutoff and monitoring foundation | 0.626 | 0.253 | 0.180 |
| Expanded IV-weighted WOE formula | 331.9K enriched accepted sample | Transparent heuristic explanation benchmark | 0.765 | 0.530 | 0.400 |
| Final clean WOE-logistic scorecard | Same 331.9K enriched sample | Coefficient-estimated scorecard layer after sign/stability cleanup | 0.781 | 0.562 | 0.418 |
| Raw logistic regression challenger | Same 331.9K enriched sample | Performance benchmark | 0.793 | 0.586 | 0.440 |

Formula-first validation on 2017 test sample for the thin portfolio baseline:

| Metric | Value |
|---|---:|
| AUC | 0.626 |
| Gini | 0.253 |
| KS | 0.180 |
| Brier score | 0.173 |
| Calibration gap | 3.50 pp |

Interpretation:

- AUC 0.626 shows **moderate ranking power**, suitable for transparent segmentation, not a strong production-grade PD model.
- KS 0.180 shows **moderate separation**, useful for policy discussion but needing challenger modeling before production.
- This is appropriate for a transparent formula-first portfolio baseline and interview discussion.
- It should not be presented as an automated production approval model without stronger features, internal data, independent validation and governance approval.
- Calibration by decile can look mechanically aligned because formula PD is assigned from observed default rate by risk decile. The more meaningful calibration check is the out-of-time 2017 test sample, where the calibration gap is **+3.50 pp**, meaning observed default is higher than average predicted PD.
- Formula PD is mechanically mapped from observed default rates by risk decile in the baseline; out-of-time validation is used to check whether that mapping holds on later vintages.

Expanded enriched modeling layer:

| Model | Test AUC | Test Gini | Test KS | Test calibration gap |
|---|---:|---:|---:|---:|
| Expanded WOE formula scorecard | 0.765 | 0.530 | 0.400 | 1.69 pp |
| Final clean WOE-logistic scorecard | 0.781 | 0.562 | 0.418 | 1.81 pp |
| Logistic regression challenger | 0.793 | 0.586 | 0.440 | 1.44 pp |

Interpretation:

- The thin 1.3M-row baseline remains useful for portfolio target definition, cutoff economics, expected loss and governance.
- The enriched accepted-loan sample adds stronger application-time drivers and materially improves model ranking.
- The expanded WOE formula scorecard is a transparent IV-weighted heuristic scoring layer, not a coefficient-estimated logistic scorecard.
- The final clean WOE-logistic scorecard uses WOE-transformed inputs, logistic coefficients and scorecard points after removing variables with severe sign/stability issues.
- The logistic regression challenger improves performance, but the expanded WOE formula scorecard remains the main explanation layer because it is transparent and policy-friendly.
- `sub_grade` and `int_rate` are excluded from the feature set because they can reflect lender pricing/risk decisions.
- `term_band_exp` is retained because it is available at origination and represents product tenor, but it is treated as policy-sensitive due to high IV.
- Enriched IV values are calculated on the 183,002-row training window only. Validation 2016 and test 2017 are reserved for out-of-time checking.

Term sensitivity:

| Model | Features | Test AUC | Test KS | Comment |
|---|---|---:|---:|---|
| Expanded WOE with term | 15 selected WOE features | 0.765 | 0.400 | Current formula scorecard |
| Expanded WOE without term | 14 selected WOE features | 0.734 | 0.350 | Product-tenor sensitivity |
| Logistic with term | 17 candidate features | 0.793 | 0.440 | Current challenger |
| Logistic without term | 16 candidate features | 0.766 | 0.404 | Product-tenor sensitivity |

Conclusion: term contributes meaningful signal, but the model does not collapse without it. Performance remains usable without term, so enriched performance is not explained by product tenor alone.

Enriched split drift:

| Sample | Rows | Observed default | Avg formula PD | Avg logistic PD | Comment |
|---|---:|---:|---:|---:|---|
| Train <=2015 | 183,002 | 16.16% | 16.16% | 16.17% | Model development |
| Validation 2016 | 85,177 | 17.84% | 14.50% | 14.68% | Higher observed default creates under-prediction pressure |
| Test 2017 | 46,369 | 15.71% | 14.01% | 14.27% | Mild under-prediction, ranking generalizes |

Additional enriched validation evidence:

- `reports/37_logistic_calibration_by_decile.csv`
- `reports/37_enriched_feature_csi_top5.csv`
- `reports/37_enriched_score_distribution_shift.csv`
- `reports/37_enriched_binning_quality_check.csv`
- `reports/37_feature_selection_rationale.csv`
- `reports/40_final_clean_woe_logistic_scorecard_coefficients.csv`
- `reports/40_final_clean_woe_logistic_scorecard_points.csv`
- `reports/40_final_clean_woe_logistic_coefficient_sign_review.csv`
- `reports/40_benchmark_woe_logistic_scorecard_points.csv`
- `reports/40_final_clean_scorecard_exclusion_log.csv`
- `reports/40_post_coarse_model_stack_performance.csv`
- `reports/40_mort_acc_sensitivity.csv`
- `reports/40_recalibration_before_after_metrics.csv`
- `reports/40_final_model_recommendation.csv`
- `reports/38_tail_calibration_review.csv`
- `reports/38_formula_vs_woe_logistic_vs_raw_logistic_calibration.csv`
- `reports/39_woe_logistic_calibration_by_decile.csv`
- `reports/39_tail_recalibration_plan.csv`
- `reports/39_recalibrated_pd_by_decile.csv`
- `reports/39_woe_stability_after_coarse_binning.csv`
- `reports/39_final_scorecard_feature_governance_list.csv`
- `reports/38_binning_coarse_adjustment_log.csv`
- `reports/38_model_performance_after_coarse_binning.csv`
- `reports/38_challenger_decision_matrix.csv`

High-risk tail calibration:

| Sample | Decile | Avg logistic PD | Observed default | Gap | Action |
|---|---:|---:|---:|---:|---|
| Validation 2016 | 10 | 51.85% | 61.85% | 10.00 pp | Recalibrate high-risk tail before production use |
| Test 2017 | 10 | 51.62% | 58.54% | 6.92 pp | Recalibrate high-risk tail before production use |

Average calibration gap is not enough. High-risk tail calibration must be reviewed separately because decile 9-10 drives cutoff, expected loss, pricing, manual review and decline policy. Current PDs are **pre-recalibration** and should not be used for production pricing, ECL or automated cutoff decisions without approved recalibration.

Tail recalibration candidate:

| Sample | Decile | Pre-recalibration gap | Recalibrated candidate gap | Method |
|---|---:|---:|---:|---|
| Test 2017 | 10 | 6.92 pp | -3.03 pp | Validation-2016 decile-level multiplicative calibration factor |

Interpretation: the candidate recalibration reduces absolute high-risk tail underprediction on the 2017 test sample, but it is diagnostic evidence only. No final recalibrated PD is selected; production use would require independent validation and an approved calibration method.

Coarse-binning check:

- Sparse bins such as DTI tail, rare purposes, rare application type, high revolving utilization and high total-account tail are merged in the coarse-binning review.
- The post-coarse feature summary now enforces the 1,000-account minimum-count rule across candidate variables.
- The final clean WOE-logistic scorecard points are generated from the post-coarse feature set, so legacy sparse DTI and rare-purpose bins are not used as final point rows.
- `revol_util_band_exp`, `mort_acc_band_exp` and `bankruptcy_band_exp` are excluded from the final clean scorecard and documented in `reports/40_final_clean_scorecard_exclusion_log.csv`.
- Benchmark evidence is retained separately in `reports/40_benchmark_woe_logistic_scorecard_points.csv` and `reports/40_benchmark_woe_logistic_coefficient_sign_review.csv`.
- Coarse-binned formula scorecard test AUC is **0.765** and KS is **0.401**, showing the benchmark remains stable after sparse-bin cleanup.

At a 20% PD cutoff:

| Metric | Value |
|---|---:|
| Approval rate | 49.47% |
| Approved default rate | 14.64% |
| Review/decline default rate | 25.57% |
| Bad capture in review/decline | 64.07% |
| Approved EL rate | 5.23% |

Cutoff scope note: this cutoff simulation is performed on matured accepted/booked accounts. It estimates how a score-based policy would segment the booked portfolio, not the true applicant-level approval rate across all applications. Rejected applicants are handled only through reject inference sensitivity because their repayment outcomes are unobserved.

Completion pack:

| Metric | Value |
|---|---:|
| Formula tests passed | 15 / 15 |
| Acceptance items tracked | 23 / 23 |
| Severe stressed EL | 3,815,530,564 |
| Severe stressed EL rate | 18.71% |
| Lowest required pricing rate | 12.55% |
| Highest required pricing rate | 28.13% |

EAD consistency note:

- Total EAD proxy of **19.42B** represents full portfolio EAD.
- Cutoff economics uses matured eligible EAD only, where 100% approval equals **18.58B**.

EL consistency note:

- Baseline expected loss of **1.53B** represents full portfolio scope.
- Cutoff economics uses matured eligible expected loss only, where 100% approval equals **1.47B**.

Illustrative risk appetite:

- Approved default rate target: <=15%.
- Approved EL rate target: <=5.5%.
- Manual review / decline capacity: around 50% of matured book.
- Severe stress loss should remain explainable under contingency mode.

Risk grade summary:

| Risk grade | Action | Default rate | Account share |
|---|---|---:|---:|
| A - Low | Auto approve | 8.52% | 9.63% |
| B - Moderate | Approve standard | 13.88% | 19.81% |
| C - Watch | Approve with limit/pricing control | 18.34% | 20.04% |
| D - High | Manual review | 22.53% | 30.32% |
| E - Very High | Decline or require mitigants | 30.12% | 20.21% |

## Run

Reviewer quick-run without Project 0:

```bash
python scripts/06_quick_review_from_sample.py
python scripts/02_validate_project3_outputs.py
```

Author full rebuild with Project 0 data core:

```bash
set FINANCIAL_RISK_DATA_CORE=<path_to_project0_data_core>
python scripts/01_build_formula_first_engine.py
python scripts/03_build_completion_pack.py
python scripts/04_build_financial_modeling_summary.py
python scripts/08_build_enriched_scorecard_challenger.py
python scripts/06_quick_review_from_sample.py
python scripts/02_validate_project3_outputs.py
```

Internal packaging only:

Packaging scripts are kept in the author/internal source folder, not in the public recruiter package. Reviewers do not need them.

The quick-run uses the included 100k samples for inspection and sanity checks. It does not regenerate the full raw-data pipeline, enriched WOE fitting or final packaging; full rebuild requires the Project 0 data core documented in `DATA_ACCESS.md`.

## Key Outputs

Reports:

- `reports/01_population_target_summary.csv`
- `reports/03_woe_iv_variable_summary.csv`
- `reports/05_score_band_summary.csv`
- `reports/06_validation_metrics.csv`
- `reports/08_cutoff_strategy.csv`
- `reports/09_expected_loss_by_risk_grade.csv`
- `reports/10_monitoring_psi.csv`
- `reports/11_reject_inference_sensitivity.csv`
- `reports/16_credit_lifecycle_map.csv`
- `reports/17_risk_taxonomy_matrix.csv`
- `reports/18_unexpected_loss_stress_buffer.csv`
- `reports/19_vintage_analysis.csv`
- `reports/20_roll_rate_framework_matrix.csv`
- `reports/21_ifrs9_ecl_bridge.csv`
- `reports/22_stress_testing_scenarios.csv`
- `reports/23_risk_based_pricing_by_grade.csv`
- `reports/24_collections_recovery_strategy.csv`
- `reports/25_concentration_risk_by_segment.csv`
- `reports/26_model_monitoring_triggers.csv`
- `reports/27_override_policy_simulation.csv`
- `reports/28_project_scope_completion_status.csv`
- `reports/29_formula_test_cases.csv`
- `reports/30_project3_completion_summary.md`
- `reports/31_financial_modeling_kpi_summary.csv`
- `reports/31_financial_modeling_numbers_and_conclusions.md`
- `reports/34_sample_quick_review.md`
- `reports/34_sample_quick_review_summary.json`
- `reports/34_sample_quick_review_by_grade.csv`
- `reports/34_sample_quick_review_by_decile.csv`
- `reports/35_enriched_feature_iv_summary.csv`
- `reports/35_enriched_formula_selected_features.csv`
- `reports/36_challenger_model_comparison.csv`
- `reports/36_challenger_model_summary.md`
- `reports/36_challenger_acceptance_criteria.csv`
- `reports/37_population_bridge.csv`
- `reports/37_term_sensitivity_comparison.csv`
- `reports/37_enriched_split_drift_summary.csv`
- `reports/37_logistic_calibration_by_decile.csv`
- `reports/37_enriched_feature_csi_top5.csv`
- `reports/37_enriched_score_distribution_shift.csv`
- `reports/37_enriched_score_distribution_psi.csv`
- `reports/37_enriched_binning_quality_check.csv`
- `reports/37_feature_selection_rationale.csv`
- `reports/40_final_clean_woe_logistic_scorecard_coefficients.csv`
- `reports/40_final_clean_woe_logistic_scorecard_points.csv`
- `reports/40_final_clean_woe_logistic_coefficient_sign_review.csv`
- `reports/40_benchmark_woe_logistic_scorecard_coefficients.csv`
- `reports/40_benchmark_woe_logistic_scorecard_points.csv`
- `reports/40_benchmark_woe_logistic_coefficient_sign_review.csv`
- `reports/40_final_clean_scorecard_exclusion_log.csv`
- `reports/38_formula_scorecard_calibration_by_decile.csv`
- `reports/38_formula_vs_logistic_calibration_comparison.csv`
- `reports/38_formula_vs_woe_logistic_vs_raw_logistic_calibration.csv`
- `reports/38_tail_calibration_review.csv`
- `reports/38_binning_coarse_adjustment_log.csv`
- `reports/38_enriched_feature_iv_after_coarse_binning.csv`
- `reports/38_model_performance_after_coarse_binning.csv`
- `reports/38_feature_selection_governance.csv`
- `reports/38_feature_correlation_matrix.csv`
- `reports/38_redundant_feature_review.csv`
- `reports/38_woe_monotonicity_review.csv`
- `reports/38_woe_stability_train_test.csv`
- `reports/38_enriched_cutoff_strategy_formula_vs_logistic.csv`
- `reports/38_challenger_decision_matrix.csv`
- `reports/38_reject_inference_scope.csv`
- `reports/38_enriched_monitoring_triggers.csv`
- `reports/38_reason_code_mapping.csv`
- `reports/38_fairness_proxy_review.csv`
- `reports/38_governance_signoff_matrix.csv`
- `reports/39_woe_logistic_calibration_by_decile.csv`
- `reports/39_tail_recalibration_plan.csv`
- `reports/39_recalibrated_pd_by_decile.csv`
- `reports/39_woe_stability_after_coarse_binning.csv`
- `reports/39_final_scorecard_feature_governance_list.csv`
- `reports/40_recalibration_before_after_metrics.csv`
- `reports/40_post_coarse_model_stack_performance.csv`
- `reports/40_mort_acc_sensitivity.csv`
- `reports/40_final_model_recommendation.csv`
- `reports/executive_summary.md`

Visuals:

- `visuals/observed_default_by_risk_grade.png`
- `visuals/cutoff_tradeoff.png`
- `visuals/expected_loss_by_risk_grade.png`
- `visuals/psi_monitoring.png`
- `visuals/vintage_default_rate.png`
- `visuals/stress_el_by_scenario.png`
- `visuals/concentration_el_top_segments.png`
- `visuals/challenger_auc_ks_comparison.png`
- `visuals/expanded_scorecard_decile_pd.png`
- `visuals/logistic_calibration_curve.png`
- `visuals/enriched_score_distribution_shift.png`
- `visuals/formula_vs_logistic_calibration_gap.png`
- `visuals/recalibration_before_after.png`

Excel:

- `excel/Credit_Risk_Formula_Engine.xlsx`

Docs:

- `docs/methodology_note.md`
- `docs/formula_dictionary.md`
- `docs/model_card.md`
- `docs/validation_checklist.md`
- `docs/governance_and_limitations.md`
- `docs/interview_story.md`
- `docs/plan_traceability_matrix.md`
- `docs/advanced_framework_extensions.md`
- `docs/credit_lifecycle_map.md`
- `docs/risk_taxonomy_map.md`
- `docs/final_recruiter_interview_pack.md`
- `docs/risk_committee_memo.md`
- `ARTIFACT_INDEX.md`

SQL and Power BI:

- `sql/SQL_Risk_KPI_Queries.sql`
- `powerbi/data_model.md`
- `powerbi/dax_measures.md`
- `powerbi/page_layout_spec.md`
- `powerbi/visual_mapping.csv`
- `powerbi/build_steps.md`
- `powerbi/theme.json`

GitHub packaging:

- `github/repo_description.md`
- `github/github_upload_checklist.md`
- `github/release_notes_v1.md`

Public package note:

- Project folder has an index page through `index.html`, so GitHub Pages/recruiter links do not rely on directory listing.
- Internal self-audit/checklist files are not required for the public GitHub package.

## Validation Audit

Run:

```bash
python scripts/02_validate_project3_outputs.py
```

Outputs:

- `reports/validation_audit.json`
- `reports/validation_audit.md`

## Limitations

- Rejected applicant population is available, but rejected applicant default outcomes are not observed.
- Reject inference is a sensitivity analysis, not a labeled reject-inference implementation.
- Cutoff economics is a matured accepted/booked account simulation, not full applicant-level approval impact.
- True monthly DPD history is unavailable in the consumer-loan core.
- Consumer-loan recovery cashflows are unavailable.
- LGD and EAD are proxy assumptions.
- RAROC/pricing requires funding cost, operating cost, capital cost and economic capital assumptions.
- Public data is not identical to internal bank data, so this should not be claimed as production underwriting.

## Governance And Next Improvements

- Monitoring triggers cover PSI, AUC/KS drop, calibration gap, score mix shift and vintage bad-rate spikes.
- Governance ownership is split across Risk Analytics, Model Validation, Credit Policy, Risk Committee, Portfolio Risk and Model Owner.
- Fairness/proxy review should check whether variables act as protected-characteristic proxies and whether variables can be explained in an adverse-action context.
- `term_band_exp` is treated as a policy-sensitive product-tenor variable; production validation should run without-term sensitivity and governance review.
- Low-IV variables are retained for a broad portfolio benchmark, not claimed as final parsimonious production scorecard features.
- With internal bank data, the next improvements would be workout LGD, true roll-rate, override performance, behavioral CCF, full IFRS 9 ECL, observed reject-inference proxy and additional calibrated ML challengers such as gradient boosting.

## Recruiter Value

This project shows that I can move beyond tool usage and translate credit risk theory into a governed analytical workflow: target definition, WOE/IV, scorecard points, validation, calibration, cutoff strategy, expected loss, vintage monitoring, IFRS 9 bridge, stress testing, pricing, collections, concentration risk and limitations.
