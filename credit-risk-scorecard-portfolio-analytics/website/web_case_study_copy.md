# Website Case Study Copy

## Title

Credit Risk Scorecard & Portfolio Analytics

Repository folder: `03_CreditRiskDecisionEngine`

## Subtitle

End-to-end credit risk management project: formula-first PD scorecard, enriched feature benchmarking, logistic challenger comparison, cutoff strategy, expected loss, monitoring, ECL bridge, stress testing, pricing and governance.

## Hero Metrics

| Metric | Value |
|---|---:|
| Accounts analyzed | 1.35M |
| Matured accounts | 1.29M |
| Test AUC | 0.626 |
| Test KS | 0.180 |
| Expanded scorecard test AUC | 0.765 |
| Final clean WOE-logistic scorecard test AUC | 0.781 |
| Logistic challenger test AUC | 0.793 |
| Reject population | 27.6M |
| Formula tests | 15 / 15 pass |
| Severe stressed EL | 3.82B |
| Portfolio EAD proxy | 19.42B |
| Baseline expected loss | 1.53B |
| 20% cutoff approved EL | 511.29M |

## Scope Consistency

- EAD consistency note: 19.42B is full portfolio EAD proxy; cutoff economics uses matured eligible EAD where 100% approval equals 18.58B.
- EL consistency note: 1.53B baseline expected loss uses full portfolio scope; cutoff economics uses matured eligible expected loss where 100% approval equals 1.47B.
- Population bridge: AUC 0.626 is the thin baseline on the 1.3M portfolio base; AUC 0.765 / 0.793 are enriched modeling benchmarks on the 331.9K accepted-loan sample. They are not the same model on the same population.
- Cutoff scope: 49.47% approval rate is a matured accepted/booked account backtest, not true applicant-level approval impact across all applications.
- Data-backed/proxy scope is documented in `docs/governance_and_limitations.md` and `DATA_ACCESS.md`.
- Internal self-audit/checklist files are not part of the public recruiter package.

## Recruiter Value

This project shows how I translate credit risk theory into decision-ready analytics: target definition, WOE/IV, PD bands, scorecard points, cutoff policy, expected loss, validation, vintage monitoring, IFRS 9 bridge, stress testing, risk-based pricing, concentration risk and governance.

## Results

At a 20% PD cutoff, the baseline workflow approves 49.47% of matured accounts, keeps approved default rate at 14.64%, and captures 64.07% of bad accounts in the review/decline group.

The enriched modeling layer improves the transparent scorecard to 0.765 test AUC / 0.400 KS. A final clean WOE-logistic scorecard built on post-coarse bins reaches 0.781 test AUC / 0.418 KS after excluding variables with sign/stability issues, while the raw logistic regression challenger reaches 0.793 test AUC / 0.440 KS. The formula scorecard remains the explanation layer; the logistic models are benchmark/challenger layers.

Senior validation additions:

- Post-coarse scorecard points remove legacy sparse DTI and rare-purpose bins from the final points file.
- Three-model calibration comparison is published in `reports/38_formula_vs_woe_logistic_vs_raw_logistic_calibration.csv`.
- High-risk tail recalibration candidate reduces test decile 10 gap from +6.92 pp to -3.03 pp, but remains governance-only until independently validated.
- `revol_util_band_exp`, `mort_acc_band_exp` and `bankruptcy_band_exp` are excluded from the final clean scorecard, with benchmark evidence retained separately.
- Final model recommendation is published in `reports/40_final_model_recommendation.csv`.
- Final scorecard feature governance decisions are documented in `reports/39_final_scorecard_feature_governance_list.csv`.

The final completion pack adds an Excel master workbook, numbered reports, lifecycle and taxonomy maps, stress/pricing/collections/concentration modules, and 15 formula test cases.

The financial modeling report shows all key numbers and management conclusions:

`reports/31_financial_modeling_numbers_and_conclusions.md`

Financial modeling numbers are summarized in `reports/31_financial_modeling_numbers_and_conclusions.md`.

With internal bank data, I would improve workout LGD, true roll-rate, override performance, behavioral CCF, full IFRS 9 ECL, observed reject-inference proxy and additional calibrated ML challengers.

## Limitations

Reject outcomes, monthly DPD history, consumer recovery cashflows, collection actions and full RAROC cost inputs are not observed. These are handled as sensitivity analysis, framework design or assumptions.
