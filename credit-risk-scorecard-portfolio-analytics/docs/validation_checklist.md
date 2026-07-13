# Validation Checklist

| Check | Status | Evidence |
|---|---|---|
| Matured accounts only used for observed default rate | Pass | `reports/01_population_target_summary.csv` |
| Good/bad/indeterminate logic defined | Pass | Project 0 master account base |
| WOE uses smoothing to avoid LN(0) | Pass | `reports/03_woe_iv_variable_summary.csv` |
| PD is between 0 and 1 | Pass | `reports/04_decile_pd_mapping.csv` |
| Score high means lower risk | Pass | Risk grades show lower score for higher PD |
| AUC calculated | Pass | `reports/06_validation_metrics.csv` |
| Gini calculated | Pass | `reports/06_validation_metrics.csv` |
| KS calculated | Pass | `reports/06_validation_metrics.csv` |
| Brier score calculated | Pass | `reports/06_validation_metrics.csv` |
| Calibration gap calculated | Pass | `reports/06_validation_metrics.csv` |
| Cutoff strategy tested | Pass | `reports/08_cutoff_strategy.csv` |
| Portfolio EL equals account-level EL aggregation | Pass | `reports/09_expected_loss_by_risk_grade.csv` |
| PSI monitoring produced | Pass | `reports/10_monitoring_psi.csv` |
| Reject inference limitation documented | Pass | `reports/11_reject_inference_sensitivity.csv` |
| Enriched challenger benchmark calculated | Pass | `reports/36_challenger_model_comparison.csv` |
| Three-model calibration comparison produced | Pass | `reports/38_formula_vs_woe_logistic_vs_raw_logistic_calibration.csv` |
| Coarse-binning minimum-count rule checked | Pass | `reports/38_enriched_feature_iv_after_coarse_binning.csv` |
| Final clean scorecard points rebuilt after coarse-binning | Pass | `reports/40_final_clean_woe_logistic_scorecard_points.csv` |
| Final clean coefficient sign review completed | Pass | `reports/40_final_clean_woe_logistic_coefficient_sign_review.csv` |
| Benchmark sign/stability exclusions documented | Pass | `reports/40_final_clean_scorecard_exclusion_log.csv` |
| Tail recalibration diagnostic produced | Conditional Pass | `reports/39_tail_recalibration_plan.csv`, `reports/39_recalibrated_pd_by_decile.csv`, `reports/40_recalibration_before_after_metrics.csv`; no final recalibrated PD is selected |
| Recalibration before/after evaluated | Conditional Pass | `reports/40_recalibration_before_after_metrics.csv` |
| Final model recommendation documented | Pass | `reports/40_final_model_recommendation.csv` |

## Current Test Metrics

| Metric | Test 2017 |
|---|---:|
| AUC | 0.626 |
| Gini | 0.253 |
| KS | 0.180 |
| Brier Score | 0.173 |
| Calibration Gap | 3.50 pp |

## Interpretation

The formula-first score has moderate ranking power. It is appropriate as a transparent baseline and interview-ready risk engine. It should not be presented as a final production underwriting model.

Calibration caveat:

- Calibration by decile can look close because formula PD is assigned from observed default rate by risk decile.
- The out-of-time 2017 test sample is the more meaningful calibration view.
- Test 2017 calibration gap is **+3.50 pp**, meaning observed default is higher than average predicted PD.
- High-risk tail PD remains pre-recalibration. The candidate validation-factor recalibration reduces test decile 10 gap from **+6.92 pp** to **-3.03 pp**, but it is not production-approved.
- The candidate recalibration over-corrects several lower/mid deciles; it is evidence of recalibration discipline, not a final calibrated PD solution.
