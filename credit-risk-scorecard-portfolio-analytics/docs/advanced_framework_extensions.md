# Advanced Framework Extensions

This note captures the senior-level additions from the supplemental Project 3 guidance. These items are included as framework, sensitivity or proxy modules when observed data is unavailable.

## Reject Inference

Rejected applicants are available through LendingClub RejectStats, but their default outcomes are not observed.

Correct treatment:

```text
Reject inference is a sensitivity experiment, not a true labeled reject model.
```

This is the reject inference sensitivity module for the current Project 3 build.

Use scenarios such as:

- 1.0x approved/booked bad rate
- 1.5x approved/booked bad rate
- 2.0x approved/booked bad rate
- 3.0x approved/booked bad rate

Do not state that rejects are "usually" 2-3x riskier as a rule. Reject bad rate depends on policy, channel, product, macro period and applicant quality.

## Missing, Outlier And Binning Rules

Rules used in the data foundation:

- Missing values are preserved as risk signals when meaningful.
- Income <= 0 is flagged as invalid.
- DTI > 100 is capped/flagged into an extreme bin instead of blindly deleted.
- Missing values can receive Missing/Unknown bins.
- Outliers should be capped only when they are likely measurement errors.

WOE smoothing:

```text
Adjusted_Good = Good_bin + 0.5
Adjusted_Bad = Bad_bin + 0.5
```

Smoothing avoids `LN(0)` and reduces inflated IV from tiny bins.

## Monotonicity And Coarse Binning

Do not mechanically force all variables to be monotonic. Some risk drivers are naturally non-monotonic.

Coarse binning should consider:

- Minimum sample size
- Stable bad rate
- Business meaning
- WOE not too extreme
- Missing value treatment
- Policy usability

## LGD And EAD

Core project treatment:

- LGD is a documented proxy assumption.
- EAD is a loan amount proxy for a term-loan style dataset.

Do not describe a fixed LGD as a universal Basel standard. LGD depends on exposure type, collateral, seniority, recovery process and regulatory approach.

Workout LGD formula if recovery cashflows become available:

```text
Discounted_Recoveries = SUM(Recovery_Cashflow_t / (1 + EIR)^t)
Workout_LGD = (EAD - Discounted_Recoveries + Collection_Costs) / EAD
```

Behavioral CCF applies only to revolving products:

```text
CCF = (EAD_at_Default - Current_Outstanding) / Undrawn_Limit
EAD = Current_Outstanding + CCF x Undrawn_Limit
```

For amortizing term loans, EAD is usually based on outstanding balance at default.

## PIT, TTC And Forward-Looking PD

Correct treatment:

- Credit decisioning PD can be PIT, TTC or hybrid depending on design and use case.
- IFRS 9 ECL generally requires point-in-time, probability-weighted, forward-looking PD/ECL.
- Regulatory capital PD is often closer to long-run/TTC calibration.
- Stress testing uses stressed or scenario-conditioned PD.

## Override Management Framework

Real credit decisions include policy rules, manual review and exception approval.

Override types:

- Hard override: system says decline, officer approves.
- Soft override: system suggests limit/pricing/action, officer changes it.

Metrics:

- Override rate
- Hard override rate
- Soft override rate
- Override bad rate
- Override approval rate
- Manual review approval rate
- Manual review bad rate
- Policy exception rate

For this project, override thresholds are illustrative internal risk appetite assumptions, not industry rules.

## PSI, CSI And Model Degradation

PSI measures overall population or score distribution shift.

CSI measures shift by individual characteristic:

```text
CSI_variable = SUM((Actual_%_bin - Expected_%_bin) x LN(Actual_%_bin / Expected_%_bin))
```

Use CSI to explain which variable caused PSI movement.

Performance metrics such as AUC, KS and Gini should be calculated only after the performance window has matured.

For recent cohorts, use early warning indicators:

- Approval mix
- Average PD
- Risk-grade mix
- PSI
- CSI
- Early delinquency if available

## Macro Overlay And Stress Testing

Recommended simple satellite model structure:

```text
Stressed_Logit = Base_Logit
  + beta_1 x Delta_Unemployment
  + beta_2 x Delta_GDP_Growth
  + beta_3 x Delta_Inflation

Stressed_PD = 1 / (1 + EXP(-Stressed_Logit))
```

For this project, stress testing should be presented as scenario overlay unless a true macro-response model is estimated.

## SICR And IFRS 9 Bridge

SICR rules should include quantitative and qualitative triggers.

Quantitative examples:

- Current lifetime PD / origination lifetime PD >= project threshold
- Risk grade downgrade by at least 2 grades
- Current PD exceeds a high-risk threshold

Qualitative examples:

- Forbearance
- Restructuring
- Watchlist
- Adverse bureau information
- Significant income deterioration

Backstop:

- 30 DPD

Any "3x PD increase" rule should be labeled as a project assumption, not a universal IFRS 9 rule.

## Recalibration And Contingency Plan

Monitoring thresholds are internal policy assumptions:

| Metric | Stable | Watchlist | Review trigger |
|---|---:|---:|---:|
| PSI | < 0.10 | 0.10-0.25 | > 0.25 |
| AUC drop | < 0.03 | 0.03-0.05 | > 0.05 |
| KS drop | < 0.03 | 0.03-0.05 | > 0.05 |
| Calibration gap | < 5 pp | 5-10 pp | > 10 pp |

Recalibration is not automatic. A model review should identify root cause first:

- Calibration drift
- Population shift
- Policy change
- Macro shock
- Data quality issue

Contingency modes:

1. Normal: use scorecard + policy rules.
2. Watchlist: keep model running, increase manual review for borderline bands.
3. Degraded model: suspend auto-approval for high-risk or unstable segments.
4. Model/data failure: fallback to expert rule-based policy.
5. Emergency tightening: lower limits and stricter DTI/delinquency filters.
