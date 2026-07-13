# Formula Dictionary

## Default Rate

```text
Default_Rate = Bad_Accounts / Matured_Accounts
```

Use only matured accounts.

## WOE

```text
WOE_bin = LN(%Good_bin / %Bad_bin)
```

Positive WOE means the bin leans good. Negative WOE means the bin leans bad.

## IV

```text
IV_variable = SUM((%Good_bin - %Bad_bin) x WOE_bin)
```

Used to measure variable separation power and create IV-based score weights.

## Good Odds

```text
Good_Odds = (1 - PD) / PD
```

Traditional scorecards often use good odds because higher odds map to higher score.

## Scorecard Points

```text
Factor = PDO / LN(2)
Offset = Base_Score - Factor x LN(Base_Good_Odds)
Score = Offset + Factor x LN(Good_Odds)
```

Higher score means lower risk.

## Expected Loss

```text
Expected_Loss = PD x LGD x EAD
```

In this project:

- PD = formula PD from score decile
- LGD = documented assumption
- EAD = loan amount proxy

## Gini

```text
Gini = 2 x AUC - 1
```

Measures ranking power.

## KS

```text
KS = MAX(TPR - FPR)
```

Measures maximum separation between good and bad cumulative distributions.

## Brier Score

```text
Brier = AVG((PD - Default_Flag)^2)
```

Measures probability error.

## PSI

```text
PSI = SUM((Actual_% - Expected_%) x LN(Actual_% / Expected_%))
```

Used for population shift monitoring.
