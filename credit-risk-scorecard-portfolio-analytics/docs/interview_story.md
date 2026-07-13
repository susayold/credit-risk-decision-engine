# Interview Story

## 60-Second Version

I built a formula-first credit risk scorecard and portfolio analytics workflow for lending default risk. The project starts with target definition and matured-account logic, then uses WOE/IV to convert borrower and loan attributes into a transparent scorecard-style risk score. I mapped the score to PD, scorecard points, risk grades, cutoff actions and expected loss. The final output includes validation metrics, cutoff simulation, PSI monitoring, reject inference sensitivity, enriched challenger benchmarking and governance limitations.

## Problem

A lender needs to balance growth and credit loss. Approving too many risky accounts increases default and expected loss. Rejecting too many accounts reduces volume and revenue.

## Data

The core data has 1.35M accepted/booked lending accounts and 1.29M matured accounts for default analysis. Supplemental data adds 27.6M rejected applications, a richer LendingClub accepted sample and SBA charge-off reference data.

## Method

I used a formula-first scorecard approach:

1. Define good/bad/indeterminate.
2. Control maturity and leakage.
3. Calculate WOE and IV.
4. Build an IV-weighted formula score.
5. Convert PD into scorecard points.
6. Validate AUC, Gini, KS, Brier and calibration.
7. Simulate cutoffs and expected loss.

## Result

The 2017 test sample produced:

- AUC: 0.626
- Gini: 0.253
- KS: 0.180
- Brier: 0.173

At a 20% PD cutoff, the engine approves 49.47% of matured accounts, keeps approved default rate at 14.64%, and captures 64.07% of bad accounts in the review/decline group.

## Business Action

Risk grades map to actions:

- A: auto approve
- B: approve standard
- C: approve with limit/pricing control
- D: manual review
- E: decline or require mitigants

## Limitation

Rejected applicants are available as a population, but their default outcomes are not observed. Therefore reject inference is a sensitivity module, not a labeled reject model. Recovery, collections, DPD roll-rate and RAROC also require assumptions or separate data.
