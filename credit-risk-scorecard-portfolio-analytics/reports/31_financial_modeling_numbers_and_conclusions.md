# Financial Modeling Numbers And Conclusions

This report turns the Project 3 formula-first risk engine into a finance-facing view. The purpose is to show portfolio exposure, expected loss, cutoff economics, stress impact, pricing logic and management conclusions.

## KPI Summary

| metric | value | category | conclusion |
| --- | --- | --- | --- |
| Portfolio accounts | 1,347,681 | Scale | 1.35M accounts is large enough for portfolio-level risk segmentation. |
| Matured accounts | 1,291,521 | Target quality | Matured-only outcomes prevent recent accounts from being incorrectly treated as good. |
| Matured default rate | 20.16% | Credit loss risk | Base portfolio risk is material at 20.16%; cutoff and pricing control are required. |
| Total EAD proxy | 19.42B | Exposure | Total exposure proxy is the financial base for EL, stress and pricing. |
| Formula expected loss | 1.53B | Expected loss | Baseline EL is about 1.53B before final policy action. |
| Formula EL rate | 7.88% | Expected loss | Portfolio EL rate is about 7.88%, so approval policy must avoid blindly maximizing volume. |
| Test AUC | 62.64% | Model ranking | AUC is acceptable for a transparent formula-first baseline, but not strong enough for automated production approval alone. |
| Test KS | 18.00% | Model separation | KS confirms moderate separation between good and bad accounts. |
| 20% cutoff approval rate | 49.47% | Policy | Approves about half the matured book while keeping higher-risk accounts in review/decline. |
| 20% cutoff approved default rate | 14.64% | Policy | Approved default rate drops below portfolio average. |
| 20% cutoff approved EAD | 9.78B | Exposure approved | At this cutoff the engine approves about 9.78B EAD. |
| 20% cutoff approved EL | 511.29M | Loss approved | Approved EL is about 511M, or 5.23% of approved EAD. |
| Bad capture in review/decline | 64.07% | Risk control | The review/decline group captures 64.07% of bad accounts. |
| Severe stressed EL | 3.82B | Stress testing | Severe scenario EL rises to about 3.82B, showing material downside sensitivity. |
| Severe stressed EL rate | 18.71% | Stress testing | Stress EL rate reaches 18.71%, requiring contingency policy. |
| Lowest required rate | 12.55% | Pricing | Low-risk grade still needs about 12.55% required rate under assumptions. |
| Highest required rate | 28.13% | Pricing | Very-high-risk grade needs about 28.13%, supporting decline/mitigant action. |
| Formula tests passed | 15 | Controls | Formula logic has test evidence instead of only visual storytelling. |

## Score Band Economics

| Risk grade | Action | Accounts | Account share | Default rate | Avg PD | Avg score | EAD | Expected loss | EL rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A - Low | Auto approve | 124,390 | 9.63% | 8.52% | 8.52% | 555 | 2.01B | 51.38M | 2.56% |
| B - Moderate | Approve standard | 255,787 | 19.81% | 13.88% | 13.88% | 516 | 4.08B | 200.88M | 4.92% |
| C - Watch | Approve with limit/pricing control | 258,759 | 20.04% | 18.34% | 18.34% | 492 | 3.69B | 259.04M | 7.02% |
| D - High | Manual review | 391,570 | 30.32% | 22.53% | 22.53% | 473 | 5.38B | 510.43M | 9.50% |
| E - Very High | Decline or require mitigants | 261,015 | 20.21% | 30.12% | 30.12% | 445 | 3.43B | 450.80M | 13.15% |

Conclusion: score bands are economically meaningful because default rate, EL rate and required action increase as score quality weakens.

## Cutoff Strategy Economics

| PD cutoff | Approved accounts | Approval rate | Approved default rate | Review/decline default rate | Bad capture review/decline | Approved EAD | Approved EL | Approved EL rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 10.00% | 124,390 | 9.63% | 8.52% | 21.40% | 95.93% | 2.01B | 51.38M | 2.56% |
| 15.00% | 380,177 | 29.44% | 12.13% | 23.52% | 82.30% | 6.09B | 252.25M | 4.14% |
| 20.00% | 638,936 | 49.47% | 14.64% | 25.57% | 64.07% | 9.78B | 511.29M | 5.23% |
| 25.00% | 1,030,506 | 79.79% | 17.64% | 30.12% | 30.20% | 15.15B | 1.02B | 6.74% |
| 35.00% | 1,291,521 | 100.00% | 20.16% |  | 0.00% | 18.58B | 1.47B | 7.92% |

Conclusion: the 20% cutoff is a balanced portfolio policy point. It approves roughly half the portfolio while still capturing most bad accounts in review/decline.

Scope consistency note: baseline expected loss of 1.53B uses full portfolio scope, while cutoff economics uses matured eligible expected loss where 100% approval equals 1.47B.

## Stress Testing

| Scenario | Accounts | Stressed EAD | Stressed EL | Stressed EL rate |
| --- | --- | --- | --- | --- |
| Base | 1,347,681 | 19.42B | 1.53B | 7.88% |
| Mild Downturn | 1,347,681 | 19.42B | 1.93B | 9.93% |
| Adverse | 1,347,681 | 19.81B | 2.62B | 13.24% |
| Severe | 1,347,681 | 20.39B | 3.82B | 18.71% |

Conclusion: severe stress creates a material expected-loss uplift and should trigger contingency actions such as tighter DTI, lower limits and more manual review.

## Risk-Based Pricing

| Risk grade | EL rate | Funding | OpEx | Capital cost | Profit margin | Required rate | Offered rate | RAROC proxy |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A - Low | 2.55% | 4.50% | 2.50% | 1.00% | 2.00% | 12.55% | 13.55% | 75.00% |
| B - Moderate | 4.92% | 4.50% | 2.50% | 1.50% | 2.00% | 15.42% | 16.42% | 50.00% |
| C - Watch | 7.02% | 4.50% | 2.50% | 2.50% | 2.00% | 18.52% | 19.52% | 37.50% |
| D - High | 9.49% | 4.50% | 2.50% | 4.00% | 2.00% | 22.49% | 23.49% | 27.27% |
| E - Very High | 13.13% | 4.50% | 2.50% | 6.00% | 2.00% | 28.13% | 29.13% | 20.00% |

Conclusion: pricing must increase with EL and capital cost. If required rate is not commercially feasible, decline or mitigants are more rational than approval.

## IFRS 9 ECL Bridge

| Stage | Accounts | EAD | Base/12m ECL | Lifetime ECL proxy | Base ECL rate | Lifetime ECL rate |
| --- | --- | --- | --- | --- | --- | --- |
| Stage 1 | 1,078,423 | 15.23B | 1.18B | 1.18B | 7.72% | 7.72% |
| Stage 2 | 9 | 18.12K | 4.69K | 11.73K | 25.88% | 64.71% |
| Stage 3 | 269,249 | 4.19B | 362.60M | 1.27B | 8.66% | 30.32% |

Conclusion: Stage 3 and lifetime ECL proxy are useful as a bridge, but this is not an audited IFRS 9 model because public data lacks true lifetime PD and SICR history.

## Top Concentration Risks

| Segment type | Segment | Accounts | Default rate | EAD | Expected loss | EL share | Flag |
| --- | --- | --- | --- | --- | --- | --- | --- |
| purpose | debt_consolidation | 781,206 | 21.34% | 11.89B | 979.01M | 63.99% | High concentration |
| fico_band | C | 460,588 | 25.44% | 5.98B | 709.92M | 46.40% | High concentration |
| fico_band | B | 608,501 | 19.89% | 9.09B | 668.82M | 43.71% | High concentration |
| income_band | 60k-100k | 480,139 | 19.37% | 7.66B | 602.24M | 39.36% | High concentration |
| risk_grade | D - High | 404,304 | 22.53% | 5.55B | 526.95M | 34.44% | High concentration |
| income_band | 30k-60k | 510,781 | 22.16% | 5.64B | 503.96M | 32.94% | High concentration |
| risk_grade | E - Very High | 269,536 | 30.12% | 3.55B | 466.50M | 30.49% | High concentration |
| purpose | credit_card | 295,551 | 17.11% | 4.38B | 334.09M | 21.84% | High concentration |
| risk_grade | C - Watch | 269,536 | 18.34% | 3.84B | 269.74M | 17.63% | Normal |
| income_band | 100k-150k | 186,423 | 16.64% | 3.73B | 257.15M | 16.81% | Normal |
| state | CA | 196,805 | 19.79% | 2.89B | 225.29M | 14.72% | Normal |
| risk_grade | B - Moderate | 269,536 | 13.88% | 4.29B | 211.21M | 13.80% | High concentration |

Conclusion: concentration analysis prevents the portfolio from being managed only by average PD. Large EAD/EL segments need exposure limits and additional segmentation.

## Worst Matured Vintages

| Vintage month | Accounts | Bad accounts | Vintage bad rate | Avg PD | Expected loss | EL rate |
| --- | --- | --- | --- | --- | --- | --- |
| 2016-07 | 21,724 | 5,781 | 26.61% | 20.43% | 24.75M | 8.16% |
| 2016-05 | 18,106 | 4,739 | 26.17% | 20.87% | 21.37M | 8.20% |
| 2016-08 | 22,258 | 5,822 | 26.16% | 20.40% | 25.78M | 8.17% |
| 2016-04 | 24,099 | 6,171 | 25.61% | 20.47% | 27.58M | 7.96% |
| 2017-09 | 13,372 | 3,339 | 24.97% | 19.69% | 15.22M | 7.78% |
| 2016-12 | 19,366 | 4,827 | 24.93% | 20.53% | 22.10M | 8.19% |
| 2016-09 | 16,906 | 4,202 | 24.86% | 20.10% | 18.95M | 7.98% |
| 2016-06 | 20,732 | 5,040 | 24.31% | 19.92% | 23.67M | 7.85% |
| 2016-11 | 18,994 | 4,610 | 24.27% | 20.31% | 21.42M | 8.04% |
| 2017-07 | 14,942 | 3,598 | 24.08% | 19.88% | 16.33M | 7.90% |

Conclusion: vintage monitoring shows when booked cohorts deteriorate and is essential for post-policy monitoring.

## Final Management Conclusions

1. At the 20% PD cutoff, the engine approves 49.47% of matured accounts and 9.78B EAD, while keeping approved EL rate at 5.23%.
2. The review/decline population captures 64.07% of bad accounts, so the cutoff is doing real risk control rather than only reducing volume.
3. High-risk grades D and E hold 47.38% of matured EAD but produce 65.28% of matured expected loss; this supports manual review, mitigants, pricing control or decline.
4. Debt consolidation is the largest concentration: 11.89B EAD and 63.99% of expected loss. This segment needs portfolio limits or tighter sub-segmentation.
5. Under severe stress, expected loss increases from 1.53B to 3.82B. That is a 2.49x loss multiple, so contingency policy should suspend auto-approval for unstable/high-risk segments.
6. Required pricing rises from 12.55% in low-risk grade to 28.13% in very-high-risk grade. If the market cannot bear the high-risk required rate, decline/mitigants are economically justified.
7. This is still a public-data model: true production use would require internal DPD history, recovery cashflows, cost of funds, capital methodology, override records and independent validation.

## Interview Message

The formula-first risk engine is useful because it connects credit-risk formulas to money: exposure approved, expected loss accepted, loss avoided through review/decline, stressed loss under downturn scenarios, required pricing by grade, and portfolio concentration controls.