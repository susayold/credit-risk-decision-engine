# Methodology Note

## Objective

Build a formula-first credit risk scorecard and portfolio analytics workflow for consumer lending default risk.

The project starts from risk logic rather than model complexity. The goal is to show how a lender can define good/bad outcomes, rank accounts by default risk, convert risk to scorecard points, choose cutoffs and connect the result to expected loss.

## Population

Core population:

- Accepted/booked consumer lending accounts
- 1,347,681 total rows
- 1,291,521 matured rows
- 56,160 monitor-only rows

The model target is evaluated only on matured accounts. Under-seasoned accounts are used for monitoring context but not treated as good accounts.

## Target Definition

Good account:

```text
Matured_Flag = 1 and Default_Flag = 0
```

Bad account:

```text
Matured_Flag = 1 and Default_Flag = 1
```

Indeterminate account:

```text
Matured_Flag = 0
```

This protects the project from maturity bias.

## Formula Engine

Candidate risk drivers are binned and evaluated with WOE/IV. Each account receives WOE values for the selected variables:

- FICO band
- DTI bin
- Income bin
- Purpose
- Home ownership
- High DTI flag
- High amount flag

Variable IV is converted into an IV weight. The score is:

```text
Good_WOE_Score = SUM(IV_Weight_variable x WOE_bin)
Risk_Score_Raw = -Good_WOE_Score
```

Higher `Risk_Score_Raw` means higher default risk.

## PD And Scorecard Points

Formula PD is derived by mapping risk deciles to observed default rates on matured accounts.

Scorecard points use good-odds convention:

```text
Good_Odds = (1 - PD) / PD
Factor = PDO / LN(2)
Offset = Base_Score - Factor x LN(Base_Good_Odds)
Score = Offset + Factor x LN(Good_Odds)
```

This project uses:

- Base score: 600
- Base good odds: 20
- PDO: 50

## Validation

Validation is time-aware:

- Train/pre-2016 sample
- 2016 validation sample
- 2017 test sample

Metrics:

- AUC
- Gini
- KS
- Brier score
- Calibration gap

## Business Decision

PD cutoffs are simulated to compare:

- Approval rate
- Approved default rate
- Review/decline default rate
- Bad capture in review/decline
- Approved expected loss rate

The 20% PD cutoff is used as the first business reference point, not as a final production policy.
