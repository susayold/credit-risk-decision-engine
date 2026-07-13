# DAX Measures

## Score Band Measures

```DAX
Accounts = SUM(ScoreBandSummary[accounts])

Bad Accounts = SUM(ScoreBandSummary[bad_accounts])

Observed Default Rate =
DIVIDE([Bad Accounts], [Accounts])

EAD Proxy = SUM(ScoreBandSummary[ead_proxy])

Expected Loss = SUM(ScoreBandSummary[expected_loss])

EL Rate = DIVIDE([Expected Loss], [EAD Proxy])
```

## Cutoff Measures

```DAX
Approval Rate = AVERAGE(CutoffStrategy[approval_rate])

Approved Default Rate = AVERAGE(CutoffStrategy[approved_default_rate])

Review Decline Default Rate =
AVERAGE(CutoffStrategy[review_or_decline_default_rate])

Bad Capture Review Decline =
AVERAGE(CutoffStrategy[bad_capture_in_review_or_decline])
```

## Validation Measures

```DAX
AUC = AVERAGE(ValidationMetrics[auc])

Gini = AVERAGE(ValidationMetrics[gini])

KS = AVERAGE(ValidationMetrics[ks])

Brier Score = AVERAGE(ValidationMetrics[brier_score])

Calibration Gap = AVERAGE(ValidationMetrics[calibration_gap])
```

## Monitoring Measures

```DAX
PSI = AVERAGE(MonitoringPSI[psi_vs_2015])

Default Rate = AVERAGE(MonitoringPSI[default_rate])

Average PD = AVERAGE(MonitoringPSI[avg_pd])
```

## Vintage Measures

```DAX
Vintage Accounts = SUM(VintageAnalysis[accounts])

Vintage Matured Accounts = SUM(VintageAnalysis[matured_accounts])

Vintage Bad Accounts = SUM(VintageAnalysis[bad_accounts])

Vintage Bad Rate =
DIVIDE([Vintage Bad Accounts], [Vintage Matured Accounts])

Vintage Expected Loss = SUM(VintageAnalysis[expected_loss])

Vintage EL Rate =
DIVIDE([Vintage Expected Loss], SUM(VintageAnalysis[ead]))
```

## Stress Measures

```DAX
Stressed EAD = SUM(StressScenarios[stressed_ead])

Stressed Expected Loss = SUM(StressScenarios[stressed_el])

Stressed EL Rate =
DIVIDE([Stressed Expected Loss], [Stressed EAD])

Average Stressed PD =
AVERAGE(StressScenarios[avg_stressed_pd])
```

## Pricing Measures

```DAX
Required Rate = AVERAGE(RiskBasedPricing[required_rate])

Illustrative Offered Rate =
AVERAGE(RiskBasedPricing[illustrative_offered_rate])

RAROC Proxy =
AVERAGE(RiskBasedPricing[raroc_proxy])
```

## Concentration Measures

```DAX
Concentration EAD = SUM(ConcentrationRisk[ead])

Concentration Expected Loss =
SUM(ConcentrationRisk[expected_loss])

EAD Share = AVERAGE(ConcentrationRisk[ead_share])

EL Share = AVERAGE(ConcentrationRisk[el_share])
```

## Test Evidence Measures

```DAX
Formula Tests Passed =
CALCULATE(COUNTROWS(FormulaTests), FormulaTests[status] = "PASS")

Formula Tests Total =
COUNTROWS(FormulaTests)

Acceptance Items =
COUNTROWS(AcceptanceStatus)
```
