# Power BI Data Model

## Tables

| Table | Source | Grain | Purpose |
|---|---|---|---|
| `ScoreBandSummary` | `reports/05_score_band_summary.csv` | Risk grade + policy action | Risk-band performance |
| `ValidationMetrics` | `reports/06_validation_metrics.csv` | Sample period | AUC, Gini, KS, Brier and calibration gap |
| `CalibrationDeciles` | `reports/07_calibration_by_decile.csv` | Risk decile | PD calibration and rank ordering |
| `CutoffStrategy` | `reports/08_cutoff_strategy.csv` | PD cutoff | Approval/default trade-off |
| `ExpectedLoss` | `reports/09_expected_loss_by_risk_grade.csv` | Risk grade + policy action | EAD, EL and EL rate |
| `MonitoringPSI` | `reports/10_monitoring_psi.csv` | Year | Portfolio shift and default trend |
| `RejectInference` | `reports/11_reject_inference_sensitivity.csv` | Scenario | Reject inference sensitivity |
| `WOEIV` | `reports/03_woe_iv_variable_summary.csv` | Variable | Driver strength |
| `LifecycleMap` | `reports/16_credit_lifecycle_map.csv` | Lifecycle stage | Credit lifecycle explanation |
| `RiskTaxonomy` | `reports/17_risk_taxonomy_matrix.csv` | Risk type | Formula/metric/decision taxonomy |
| `VintageAnalysis` | `reports/19_vintage_analysis.csv` | Vintage month | Cohort bad rate and EL monitoring |
| `RollRateFramework` | `reports/20_roll_rate_framework_matrix.csv` | DPD transition | Roll-rate formula framework |
| `IFRS9ECLBridge` | `reports/21_ifrs9_ecl_bridge.csv` | Stage + FICO band | ECL bridge by IFRS 9 stage |
| `StressScenarios` | `reports/22_stress_testing_scenarios.csv` | Scenario + risk grade | Stressed PD/LGD/EAD/EL |
| `RiskBasedPricing` | `reports/23_risk_based_pricing_by_grade.csv` | Risk grade + policy action | Required pricing and RAROC proxy |
| `CollectionsStrategy` | `reports/24_collections_recovery_strategy.csv` | DPD bucket | Collection action matrix |
| `ConcentrationRisk` | `reports/25_concentration_risk_by_segment.csv` | Segment variable + value | EAD/EL concentration |
| `MonitoringTriggers` | `reports/26_model_monitoring_triggers.csv` | Metric | Trigger thresholds and management actions |
| `OverrideSimulation` | `reports/27_override_policy_simulation.csv` | Override type + policy action | Override candidate summary |
| `AcceptanceStatus` | `reports/28_project_scope_completion_status.csv` | Project scope checkpoint | Final project scope status |
| `FormulaTests` | `reports/29_formula_test_cases.csv` | Test case | Formula test evidence |

## Relationships

This dashboard can be built mostly as disconnected analytical tables because each output is already aggregated for a specific view.

Optional relationships:

- `ScoreBandSummary[risk_grade]` to `ExpectedLoss[risk_grade]`
- `ScoreBandSummary[risk_grade]` to `StressScenarios[risk_grade]`
- `ScoreBandSummary[risk_grade]` to `RiskBasedPricing[risk_grade]`
- `CutoffStrategy[pd_cutoff]` as standalone slicer
- `ValidationMetrics[sample]` as standalone sample comparison
- Most governance/reference tables can remain disconnected.

## Design Principle

Use Power BI as the business presentation layer. The risk formulas are calculated upstream by the reproducible Python engine.
