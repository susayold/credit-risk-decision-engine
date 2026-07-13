# Executive Summary - Project 3 Formula-First Credit Risk Engine

## Business Question

Which accepted/booked lending accounts are likely to default, how should they be ranked into risk bands, and what approval or review action should follow?

## Data Foundation

- Account rows: 1,347,681
- Matured rows: 1,291,521
- Monitor-only rows: 56,160
- Matured default rate: 20.16%
- Total EAD proxy: 19,417,698,475
- Formula expected loss: 1,530,037,319

## Formula Engine Result

- Test AUC: 0.626
- Test Gini: 0.253
- Test KS: 0.180
- Test Brier score: 0.173
- Test calibration gap: 3.50%

## Cutoff Strategy

At PD cutoff 20%:

- Approval rate: 49.47%
- Approved default rate: 14.64%
- Review/decline default rate: 25.57%
- Bad capture in review/decline group: 64.07%
- Approved EL rate: 5.23%

## Risk Governance Note

This is a formula-first portfolio project. Rejected applicant population is available, but rejected applicant default outcomes are not observed. Therefore reject inference is treated as sensitivity analysis, not as a labeled reject model.
