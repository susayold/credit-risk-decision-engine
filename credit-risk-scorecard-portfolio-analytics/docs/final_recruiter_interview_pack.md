# Final Recruiter Interview Pack

## One-minute pitch

This project builds a formula-first credit risk scorecard and portfolio analytics workflow for a lending portfolio. It starts with target definition and matured-account logic, then calculates WOE/IV, PD, scorecard points, expected loss, validation metrics, cutoff policy, monitoring triggers, IFRS 9 bridge, stress testing, risk-based pricing and governance documentation. The enriched modeling layer adds stronger application-time variables and benchmarks the scorecard against a logistic regression challenger.

## Value to employer

- I can define a credit-risk target correctly before modeling.
- I can translate borrower data into PD, score bands, expected loss and policy actions.
- I can validate discrimination, calibration and business cutoff trade-offs.
- I can compare a transparent scorecard with a challenger model without over-claiming production readiness.
- I can document limitations honestly instead of over-claiming public-data assumptions.
- I can package outputs for Risk, Credit Policy, Finance and Model Governance stakeholders.

## Best interview story

I did not start with machine learning first. I started with the credit-risk logic: good/bad definition, observation window, performance window and matured population. Then I used WOE/IV to understand risk drivers, built a transparent scorecard-style PD workflow, translated PD into policy actions, and connected those decisions to expected loss, monitoring and governance. After that baseline was explainable, I added an enriched scorecard and logistic challenger benchmark to show the performance trade-off.

## CV bullet

Built an end-to-end credit risk scorecard and portfolio analytics framework on 1.3M+ accepted/booked lending accounts, with an enriched accepted-loan modeling benchmark on 331.9K rows comparing expanded WOE scorecard versus logistic regression challenger.

## Acceptance status

| acceptance_criterion | status | evidence |
| --- | --- | --- |
| Credit Risk / Lending Risk project is clear | Done | README.md, website case study, business context |
| Target definition is clear | Done | reports/01_population_target_summary.csv, docs/model_card.md |
| Observation/performance window is documented | Done | docs/methodology_note.md |
| Matured account logic is implemented | Done | matured_flag, monitor_only_flag, formula test cases |
| Leakage checklist is documented | Done | docs/validation_checklist.md, project3_feature_eligibility_matrix.csv |
| Reject inference limitation is explicit | Done | reports/11_reject_inference_sensitivity.csv |
| PD, LGD, EAD, EL are available | Done with proxy assumptions | reports/09_expected_loss_by_risk_grade.csv |
| WOE, IV, odds and log odds are available | Done | reports/03_woe_iv_variable_summary.csv, docs/formula_dictionary.md |
| Scorecard and score bands are available | Done | reports/05_score_band_summary.csv |
| Credit decision rules are available | Done | reports/08_cutoff_strategy.csv, reports/27_override_policy_simulation.csv |
| Expected loss by segment is available | Done | reports/09_expected_loss_by_risk_grade.csv, reports/25_concentration_risk_by_segment.csv |
| AUC, KS, Gini, Brier are available | Done | reports/06_validation_metrics.csv |
| Enriched scorecard and logistic challenger are available | Done | reports/36_challenger_model_comparison.csv |
| Calibration gap is available | Done | reports/07_calibration_by_decile.csv |
| PSI is available | Done | reports/10_monitoring_psi.csv |
| Vintage analysis is available | Done | reports/19_vintage_analysis.csv |
| Roll-rate matrix is available | Framework only | reports/20_roll_rate_framework_matrix.csv; monthly DPD unavailable |
| IFRS 9 ECL bridge is available | Bridge only | reports/21_ifrs9_ecl_bridge.csv |
| Stress testing is available | Done with proxy assumptions | reports/22_stress_testing_scenarios.csv |
| Risk-based pricing is available | Done with assumptions | reports/23_risk_based_pricing_by_grade.csv |
| Governance and limitation pack is available | Done | docs/governance_and_limitations.md, reports/26_model_monitoring_triggers.csv |
| README can be read within 60 seconds | Done | README.md |
| Interview story is available | Done | docs/interview_story.md, docs/final_recruiter_interview_pack.md |

## Formula test results

| test_id | test_name | status | evidence |
| --- | --- | --- | --- |
| T01 | Account not matured is excluded from default rate | PASS | Monitor-only accounts do not contribute bad flags. |
| T02 | Leakage flag is controlled | PASS | Leakage flag total = 0. |
| T03 | Default Rate = Defaulted Matured Accounts / Matured Accounts | PASS | reported=0.20162506, calculated=0.20162506 |
| T04 | WOE good distribution sums to 100% by variable | PASS | {'dti_extreme_or_missing_bin': 1.0, 'fico_band': 1.0, 'high_amount_flag': 1.0, 'high_dti_flag': 1.0, 'home_ownership': 1.0, 'income_missing_or_invalid_bin': 1.0, 'purpose': 1.0} |
| T05 | WOE bad distribution sums to 100% by variable | PASS | {'dti_extreme_or_missing_bin': 1.0, 'fico_band': 1.0, 'high_amount_flag': 1.0, 'high_dti_flag': 1.0, 'home_ownership': 1.0, 'income_missing_or_invalid_bin': 1.0, 'purpose': 1.0} |
| T06 | WOE smoothing avoids infinite WOE | PASS | All smoothed WOE values are finite. |
| T07 | IV variable equals sum of IV bins | PASS | IV bin sum reconciles to variable IV. |
| T08 | PD stays between 0 and 1 | PASS | min=0.0852, max=0.3317 |
| T09 | Higher score corresponds to lower risk grade | PASS | {'A - Low': 555.1, 'B - Moderate': 515.72, 'C - Watch': 491.7, 'D - High': 473.24, 'E - Very High': 444.9} |
| T10 | Portfolio EL equals sum of account-level EL | PASS | account=1530037318.76, grade=1530037318.76 |
| T11 | Calibration Gap = Observed Default Rate - Average PD | PASS | Calibration table formula reconciles. |
| T12 | PSI is zero when actual distribution equals expected distribution | PASS | Identical distributions produce PSI 0. |
| T13 | Vintage bad rate uses matured-account denominator | PASS | Vintage formula reconciles. |
| T14 | Roll-rate denominator is defined by opening DPD bucket | PASS | All roll-rate formulas specify denominator at start. |
| T15 | IFRS 9 Stage 1 uses base/12-month ECL and Stage 2/3 use lifetime proxy | PASS | All three IFRS 9 bridge stages are present. |