# Power BI Page Layout Spec

## Page 1 - Executive Summary

Purpose: recruiter or risk manager understands the project in under 60 seconds.

Visuals:

- KPI cards: Accounts, Matured Default Rate, Test AUC, Test KS, Approval Rate at 20% cutoff, Approved EL Rate
- Bar chart: Observed Default Rate by Risk Grade
- Line chart: Cutoff trade-off
- Text box: limitation note about reject outcomes and LGD/EAD assumptions

## Page 2 - Risk Grade Performance

Purpose: show rank ordering and policy action.

Visuals:

- Matrix: Risk grade, policy action, accounts, default rate, average PD, average score, EAD, expected loss, EL rate
- Bar chart: Default rate by risk grade
- Bar chart: Expected loss by risk grade

## Page 3 - Cutoff Strategy

Purpose: show business trade-off.

Visuals:

- Line chart: Approval rate by PD cutoff
- Line chart: Approved default rate by PD cutoff
- Line chart: Bad capture in review/decline by PD cutoff
- Table: cutoff simulation

## Page 4 - Validation And Calibration

Purpose: separate ranking power from probability quality.

Visuals:

- KPI cards: AUC, Gini, KS, Brier, calibration gap
- Matrix: validation metrics by sample
- Bar/line chart: observed default rate vs average PD by risk decile

## Page 5 - Vintage And Monitoring

Purpose: show post-deployment and cohort monitoring.

Visuals:

- Line chart: PSI by year
- Line chart: default rate vs average PD by year
- Line chart: vintage bad rate by application month
- Column chart: expected loss by vintage quarter

## Page 6 - ECL And Stress Testing

Purpose: bridge credit risk model outputs into provision and stress conversations.

Visuals:

- Matrix: IFRS 9 stage, FICO band, accounts, EAD, average PD, LGD, ECL base, lifetime ECL proxy
- Clustered bar chart: stressed expected loss by scenario
- Stacked bar chart: stressed EL by risk grade and scenario
- Text box: bridge-only limitation; not audited IFRS 9 production model

## Page 7 - Pricing And Concentration

Purpose: show how risk metrics influence commercial decisions.

Visuals:

- Matrix: risk grade, EL rate, required rate, offered rate, RAROC proxy
- Bar chart: top 10 purpose segments by expected loss
- Bar chart: EAD share by risk grade
- Table: concentration flags

## Page 8 - Governance And Test Evidence

Purpose: prove the project is controlled, testable and interview-ready.

Visuals:

- KPI cards: formula tests passed, acceptance items, required files checked
- Table: formula test cases
- Table: monitoring trigger thresholds
- Table: reject inference sensitivity
- Table: data gaps and handling
