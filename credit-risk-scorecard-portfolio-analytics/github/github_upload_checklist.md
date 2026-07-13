# GitHub Upload Checklist

## Before Upload

- [ ] Confirm no raw customer/borrower names or street addresses are included.
- [ ] Keep large raw datasets out of GitHub.
- [ ] Upload code, docs, reports, visuals and Excel workbook.
- [ ] Keep `data/processed/formula_engine_account_sample.csv.gz` only if file size is acceptable.
- [ ] Confirm README explains business value in under 60 seconds.
- [ ] Confirm limitations are visible.
- [ ] Confirm README says 1.3M baseline and 331.9K enriched benchmark are not directly comparable as the same population.
- [ ] Confirm CV wording does not claim "1.3M model AUC 0.793".
- [ ] Confirm reviewer quick-run works from the public package without Project 0.
- [ ] Run `python scripts/06_quick_review_from_sample.py`.
- [ ] Run `python scripts/02_validate_project3_outputs.py`.
- [ ] Confirm `reports/validation_audit.md` says PASS.
- [ ] If doing author full rebuild, set `FINANCIAL_RISK_DATA_CORE` and then run `01`, `03`, `04`, `08`, `06`, `02` in order.
- [ ] Confirm `reports/29_formula_test_cases.csv` has 15 PASS rows.
- [ ] Confirm `excel/Credit_Risk_Formula_Engine.xlsx` opens.
- [ ] Optional: upload/extract the portable ZIP package from the author local package folder.

## Files To Include

- `README.md`
- `requirements.txt`
- `.gitignore`
- `scripts/01_build_formula_first_engine.py`
- `scripts/02_validate_project3_outputs.py`
- `scripts/03_build_completion_pack.py`
- `scripts/04_build_financial_modeling_summary.py`
- `scripts/06_quick_review_from_sample.py`
- `scripts/07_package_portable_zip.py`
- `scripts/08_build_enriched_scorecard_challenger.py`
- `reports/*.csv`
- `reports/executive_summary.md`
- `reports/30_project3_completion_summary.md`
- `reports/31_financial_modeling_numbers_and_conclusions.md`
- `reports/36_challenger_model_summary.md`
- `docs/*.md`
- `visuals/*.png`
- `excel/Credit_Risk_Formula_Engine.xlsx`
- `powerbi/*`
- `sql/SQL_Risk_KPI_Queries.sql`
- `github/*.md`
- `website/*.md`
- `ARTIFACT_INDEX.md`

## Files Not To Include

- Raw ZIP files
- Raw SBA files
- Full Project 0 data core
- Any `.pbix` file unless intentionally published
- Any private resume or personal identifier
- Internal review-only validation artifacts created outside the public recruiter package
- Raw/noisy reject `loan_title` sample exports such as `reports/14_reject_segment_summary_sample.csv`

## Suggested First Commit

```bash
git init
git add .
git commit -m "Build credit risk scorecard portfolio analytics"
```
