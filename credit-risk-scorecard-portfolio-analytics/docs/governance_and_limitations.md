# Governance And Limitations

## Intended Use

- Credit risk modeling portfolio project
- Scorecard mechanics
- Cutoff simulation
- Expected loss analytics
- Monitoring and governance demonstration

## Not Intended Use

- Production credit approval
- Automated underwriting
- Regulatory capital model
- Audited IFRS 9 provisioning model
- Real bank policy deployment

## Key Limitations

| Limitation | Impact | Mitigation |
|---|---|---|
| Rejected applicants have no observed default outcome | Reject inference cannot be proven directly | Treat reject inference as sensitivity analysis |
| EAD uses loan amount proxy | Expected loss may overstate or understate exposure | Document assumption; future improvement requires outstanding balance |
| LGD is assumption-based | Expected loss is not recovery-calibrated | Use scenario LGD; future workout LGD needs recovery cashflows and collection costs |
| Monthly DPD history unavailable | True roll-rate cannot be computed | Roll-rate remains framework only; use vintage/default proxy |
| Consumer-loan recovery cashflows unavailable | Workout LGD remains assumption/framework | Add discounted recoveries and collection costs when internal data is available |
| Manual review/override records unavailable | Override bad rate cannot be measured | Override monitoring remains policy framework |
| Funding/capital cost unavailable | RAROC/pricing requires assumptions | Replace proxy assumptions with institution-owned cost/capital methodology |
| Public data only | Not identical to bank internal data | Do not claim production underwriting readiness |

## Monitoring Triggers

| Metric | Watchlist | Breach |
|---|---:|---:|
| PSI | 0.10 | 0.25 |
| AUC drop | 0.03 | 0.05 |
| KS drop | 0.03 | 0.05 |
| Calibration gap | 5 pp | 10 pp |
| Approved default rate increase | 2 pp | 5 pp |

Monitoring breaches should trigger root-cause investigation or recalibration assessment first. Recalibration, redevelopment or cutoff tightening should occur only after data quality, policy mix, macro condition and segment shift have been reviewed.

## Governance Ownership

| Item | Owner | Frequency | Action |
|---|---|---|---|
| PSI monitoring | Risk Analytics | Monthly | Watchlist / investigate |
| Calibration gap | Model Validation | Quarterly after maturity | Recalibration assessment |
| Cutoff review | Credit Policy | Monthly / quarterly | Tighten or loosen policy |
| Override review | Risk Committee | Monthly | Limit exception abuse |
| Stress testing | Portfolio Risk | Quarterly | Contingency action |
| Model card update | Model Owner | Each change | Version control |

## Fairness / Proxy Review

- Check whether variables act as proxies for protected characteristics.
- Avoid variables that cannot be explained in an adverse-action context.
- Review missing income and home ownership treatment carefully.
- Document variable business rationale and limitation.

| Variable | Proxy / fairness concern | Action |
|---|---|---|
| `home_ownership` | May proxy wealth, housing stability or socioeconomic profile. | Keep only with documented business rationale; monitor disparate impact and override behavior. |
| `income_missing` | Missingness may reflect data quality, channel behavior or applicant profile. | Use a separate missing bin; monitor approval/default impact by segment. |
| `purpose` | May correlate with social or economic profile. | Use explainable categories; avoid overly granular categories that are hard to justify. |
| `FICO band` | Core creditworthiness signal, but still requires clear source and meaning. | Keep as core risk variable; document source, binning and adverse-action explanation. |

## Challenger Model Note

This project intentionally starts with a transparent formula-first scorecard baseline. In a production setting, this baseline should be benchmarked against challenger models such as logistic regression, gradient boosting or calibrated ML. The scorecard remains valuable because it is interpretable, auditable and policy-friendly.

Challenger acceptance criteria:

- Improve AUC/KS materially versus the formula-first baseline.
- Improve ranking without worsening out-of-time calibration or Brier score.
- Maintain explainability for adverse action, policy review and business sign-off.
- Pass leakage, PSI, segment stability and monitoring trigger checks.
- Treat calibration as **Conditional Pass** when average gap is acceptable but high-risk tail gap still requires recalibration control.
- Review coefficient sign reversals before production; `revol_util_band_exp` and `bankruptcy_band_exp` are excluded from the final clean scorecard because of sign-reversal behavior.
- Review WOE stability before production; `mort_acc_band_exp` is excluded from the final clean scorecard because its post-coarse test WOE movement exceeds the remediation threshold.

## Model Risk Message

The project is valuable because it is transparent about what the data can and cannot prove. It uses actual data for target definition, WOE/IV, score bands, validation, cutoff and expected loss. It uses assumptions or sensitivity where observed data is unavailable.
