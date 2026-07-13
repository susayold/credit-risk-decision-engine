# Enriched Scorecard And Challenger Benchmark

## Why This Module Was Added

The original 1.3M-row portfolio foundation is strong for target definition, expected loss, cutoff economics and monitoring,
but its modeling feature set is intentionally thin. This enriched LendingClub accepted-loan sample adds application-time
risk drivers such as loan term, revolving utilization, open accounts, public records, bankruptcies, mortgage accounts,
employment length, verification status and application type.

## Population Bridge

The project uses three related but distinct data layers. The AUC 0.626 baseline and the AUC 0.765/0.793 enriched
models are **not directly comparable as the same model on the same population**. The baseline measures performance on
the large portfolio foundation with a thinner feature set, while the enriched models benchmark performance on a smaller
accepted-loan sample with stronger application-time variables.

| Dataset layer | Rows | Role | Not used for |
|---|---:|---|---|
| Portfolio base | 1,347,681 | Target, PD baseline, EL, cutoff, monitoring | Enriched model benchmark |
| Enriched accepted sample | 331,865 | Expanded WOE and logistic challenger | Direct comparison to 1.3M baseline as same model/population |
| Rejected applicant data | 27,648,741 | Reject inference sensitivity | Labeled reject model training |

## Data Scope

| Item | Value |
|---|---:|
| Enriched accepted-loan rows | 331,865 |
| Candidate risk features | 17 |
| Features selected into expanded formula | 15 |
| Train rows <= 2015 | 183,002 |
| Validation rows 2016 | 85,177 |
| Test rows 2017 | 46,369 |

Note: IV values are calculated on the 183,002-row training window, not on the full 331,865-row enriched sample. This prevents look-ahead bias in WOE fitting and PD mapping.

## Out-Of-Time Test Performance

| Model | AUC | Gini | KS | Calibration Gap | Brier |
|---|---:|---:|---:|---:|---:|
| Expanded WOE formula scorecard | 0.765 | 0.530 | 0.400 | 1.69% | 0.114 |
| WOE logistic scorecard | 0.781 | 0.562 | 0.418 | 1.81% | 0.110 |
| Logistic regression challenger | 0.793 | 0.586 | 0.440 | 1.44% | 0.108 |

## Classic Scorecard Caveat

The expanded WOE formula scorecard is a transparent IV-weighted heuristic scoring layer. The final clean WOE-logistic
scorecard fits logistic regression on WOE-transformed variables and provides coefficient-estimated scorecard points in
`reports/40_final_clean_woe_logistic_scorecard_points.csv`. The final public points file is rebuilt on the post-coarse-binning
feature set and excludes `revol_util_band_exp`, `mort_acc_band_exp` and `bankruptcy_band_exp` because benchmark diagnostics
found sign or stability issues. Benchmark full-scorecard evidence is retained separately in the `40_benchmark_*` reports.

## Term Sensitivity

`term_band_exp` is available at origination and is not an outcome variable, so it is retained as an application-time
product-tenor feature. However, its IV is very high, so it is treated as policy-sensitive. In production validation,
I would test whether performance depends too heavily on product-tenor segmentation.

| Model | Features | Test AUC | Test KS | Comment |
|---|---|---:|---:|---|
| Expanded WOE with term | 15 selected WOE features | 0.765 | 0.400 | Current formula scorecard |
| Expanded WOE without term | 14 selected WOE features | 0.734 | 0.350 | Product-tenor sensitivity |
| Logistic with term | 17 candidate features | 0.793 | 0.440 | Current challenger |
| Logistic without term | 16 candidate features | 0.766 | 0.404 | Product-tenor sensitivity |

## Enriched Split Drift

| Sample | Rows | Observed default | Avg formula PD | Avg logistic PD | Comment |
|---|---:|---:|---:|---:|---|
| Train <=2015 | 183,002 | 16.16% | 16.16% | 16.17% | Model development |
| Validation 2016 | 85,177 | 17.84% | 14.50% | 14.68% | Out-of-time validation |
| Test 2017 | 46,369 | 15.71% | 14.01% | 14.27% | Out-of-time test |

Enriched model drift is now documented through split default rates, score distribution PSI and top-feature CSI. Current
results support a portfolio benchmark story, while production use would still require recurring feature-level monitoring.

## Calibration And Binning Evidence Added

- Logistic calibration by decile: `reports/37_logistic_calibration_by_decile.csv`
- Formula vs logistic calibration comparison: `reports/38_formula_vs_logistic_calibration_comparison.csv`
- Three-model calibration comparison: `reports/38_formula_vs_woe_logistic_vs_raw_logistic_calibration.csv`
- WOE-logistic calibration by decile: `reports/39_woe_logistic_calibration_by_decile.csv`
- High-risk tail calibration review: `reports/38_tail_calibration_review.csv`
- Tail recalibration plan: `reports/39_tail_recalibration_plan.csv`
- Recalibrated PD by decile candidate: `reports/39_recalibrated_pd_by_decile.csv`
- Top-feature CSI: `reports/37_enriched_feature_csi_top5.csv`
- Score distribution shift: `reports/37_enriched_score_distribution_shift.csv`
- Binning quality check: `reports/37_enriched_binning_quality_check.csv`
- Feature selection rationale: `reports/37_feature_selection_rationale.csv`
- Final clean coefficient sign review: `reports/40_final_clean_woe_logistic_coefficient_sign_review.csv`
- Post-coarse WOE stability: `reports/39_woe_stability_after_coarse_binning.csv`
- Final scorecard feature governance list: `reports/39_final_scorecard_feature_governance_list.csv`
- Final clean scorecard exclusion log: `reports/40_final_clean_scorecard_exclusion_log.csv`
- Recalibration before/after metrics: `reports/40_recalibration_before_after_metrics.csv`
- Post-coarse model stack performance: `reports/40_post_coarse_model_stack_performance.csv`
- Mort-account sensitivity: `reports/40_mort_acc_sensitivity.csv`
- Final model recommendation: `reports/40_final_model_recommendation.csv`
- Coarse-binning adjustment log: `reports/38_binning_coarse_adjustment_log.csv`
- Challenger decision matrix: `reports/38_challenger_decision_matrix.csv`
- Reason code, fairness/proxy and governance sign-off matrices: `reports/38_reason_code_mapping.csv`, `reports/38_fairness_proxy_review.csv`, `reports/38_governance_signoff_matrix.csv`

## High-Risk Tail Calibration

Average calibration gap is not enough. High-risk tail calibration must be reviewed separately because decile 9-10 drives
cutoff, expected loss, pricing, manual review and decline policy. Current PDs are pre-recalibration and should not be used
for production pricing, ECL or automated cutoff decisions without approved recalibration. A candidate validation-factor
recalibration table is provided; for test decile 10 it moves the gap from 6.92%
to -3.03%. The before/after metrics also show that this method can
over-correct lower and mid deciles, so it is diagnostic evidence only; no final recalibrated PD is selected.

## Coarse-Binning And Final Candidate Controls

The coarse-binning pass now enforces the 1,000-account minimum-count rule in the post-coarse feature summary. DTI tail
bins are merged into `30+`, rare loan purposes are merged into `other`, and the sparse/low-IV application-type variable
is collapsed before final scorecard feature-governance review. The WOE-logistic scorecard points file is generated from this
post-coarse feature set. The final clean portfolio-demonstration WOE-logistic layer removes `revol_util_band_exp`, `mort_acc_band_exp` and
`bankruptcy_band_exp`; the full benchmark version is kept only as diagnostic evidence.

`reports/40_final_clean_woe_logistic_coefficient_sign_review.csv` checks whether final clean coefficients are directionally consistent
with the WOE convention `WOE = ln(%Good / %Bad)` and `target = bad_flag`. The benchmark sign review is retained separately
in `reports/40_benchmark_woe_logistic_coefficient_sign_review.csv` to show why exclusions were made.

## Senior Interpretation

- The expanded WOE formula scorecard materially improves ranking power versus the thin 1.3M-row baseline.
- Logistic regression is a valid challenger because it improves AUC/KS, but it is kept as a benchmark rather than the primary public story.
- The final clean scorecard remains the explanation layer because it is easier to audit, map to policy, discuss with credit officers and support adverse-action style reasoning.
- `sub_grade` and `int_rate` are deliberately excluded because they can encode lender pricing/risk decisions and create leakage-like contamination.
- `term_band_exp` is retained as a business-valid origination variable, but treated as policy-sensitive due to high IV.
- A production model is not selected from this public dataset; it would require independent validation, ongoing PSI/calibration monitoring, adverse-action review and approval from model governance.

## Selected Feature Themes

The final clean scorecard drivers are product tenor, FICO band, DTI, verification status, loan amount, home ownership,
income band, purpose, open accounts, employment length, public records and revolving balance. Mortgage-account,
revolving-utilization and bankruptcy variables are retained only as benchmark/diagnostic evidence until remediated.
