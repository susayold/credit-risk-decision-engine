# Risk Committee Memo - Project 3

## Objective

Assess a public-data credit risk scorecard and portfolio analytics workflow for recruiter-facing demonstration, not production deployment.

## Data Scope

- Portfolio base: 1.35M accepted/booked accounts for target, EL, cutoff and monitoring.
- Enriched accepted sample: 331.9K rows for expanded WOE scorecard, WOE-logistic scorecard and raw logistic challenger.
- Rejected applicants: 27.6M records for reject inference sensitivity only; no observed repayment outcome.

## Key Findings

- Thin portfolio baseline has moderate ranking power: AUC 0.626, KS 0.180.
- Expanded WOE formula scorecard improves to AUC 0.765, KS 0.400.
- WOE logistic scorecard, the classic coefficient-estimated scorecard layer, achieves AUC 0.781, KS 0.418.
- Raw logistic challenger achieves AUC 0.793, KS 0.440.
- Removing term reduces formula AUC to 0.734 and logistic AUC to 0.766, showing product tenor is important but not the only signal.

## Calibration And Tail Risk

Average calibration is acceptable for a portfolio benchmark, but high-risk tail gap reaches 10.00%. Decile 9-10 should be recalibrated before any production use.

## Cutoff Recommendation

The 20% PD cutoff in the baseline is a booked-account simulation only. It should be used to discuss segmentation and expected loss, not as a true applicant-level approval strategy.

## Required Approvals Before Production

- Feature approval from Credit Risk and Compliance.
- Binning approval from Model Development.
- Independent validation from Model Risk.
- Cutoff approval from Credit Policy.
- Monitoring trigger approval from Portfolio Risk.
- Final production approval from Risk Committee.

## Committee Position

Use this project as a portfolio demonstration of risk analytics judgment. Do not use for automated underwriting, pricing, credit limit assignment or IFRS 9 reporting without independent validation, recalibration, production data lineage, adverse-action review and governance approval.
