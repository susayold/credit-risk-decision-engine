# Release Notes - v1 End-to-End Formula-First Completion

## Release Summary

Project 3 now has a reproducible formula-first credit risk scorecard and portfolio analytics workflow plus senior risk-management completion modules.

## Included

- Matured good/bad target logic
- WOE/IV driver summary
- IV-weighted formula score
- Formula PD by risk decile
- Scorecard points using good-odds convention
- Risk grades and policy actions
- AUC, Gini, KS, Brier and calibration metrics
- Cutoff strategy simulation
- Expected loss by risk grade
- PSI monitoring
- Reject inference sensitivity
- Governance and limitation docs
- Credit lifecycle map
- Credit risk taxonomy map
- Vintage analysis
- Roll-rate framework matrix
- IFRS 9 ECL bridge
- Stress testing scenarios
- Risk-based pricing and RAROC proxy
- Collections and recovery strategy
- Concentration risk table
- Override policy simulation
- Monitoring trigger framework
- Excel master workbook
- Formula test cases
- Financial modeling numbers and management conclusions
- Enriched scorecard and logistic challenger benchmark
- Data-backed/proxy scope and governance limitations
- Final recruiter interview pack
- Power BI build specification
- SQL KPI query pack
- Website copy

## Headline Metrics

| Metric | Value |
|---|---:|
| Accounts | 1,347,681 |
| Matured accounts | 1,291,521 |
| Matured default rate | 20.16% |
| Test AUC | 0.626 |
| Test KS | 0.180 |
| Test Brier score | 0.173 |
| Expanded scorecard test AUC | 0.765 |
| Expanded scorecard test KS | 0.400 |
| Logistic challenger test AUC | 0.793 |
| Logistic challenger test KS | 0.440 |
| 20% cutoff approval rate | 49.47% |
| 20% cutoff approved default rate | 14.64% |
| Bad capture in review/decline | 64.07% |
| Rejected applicant population | 27,648,741 |
| Formula tests passed | 15 / 15 |
| Severe stressed EL | 3,815,530,564 |
| Severe stressed EL rate | 18.71% |
| Portfolio EAD proxy | 19.42B |
| Baseline expected loss | 1.53B |
| 20% cutoff approved EAD | 9.78B |
| 20% cutoff approved EL | 511.29M |

## Known Limitations

- Reject default outcomes are not observed.
- True monthly DPD roll-rate is not available in the core consumer-loan data.
- Consumer-loan recovery cashflows are not available.
- LGD/EAD are proxy assumptions.
- Risk-based pricing and RAROC use funding, operating, capital cost and margin assumptions.

## Next Version

- Add Power BI screenshots after manual `.pbix` build.
- Add optional gradient boosting or calibrated ML challenger after reviewing the scorecard benchmark.
