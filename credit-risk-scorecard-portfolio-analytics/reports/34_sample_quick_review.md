# Sample Quick Review

Mode: **light sample review**

This report is generated from `data/processed/formula_engine_account_sample.csv.gz`. It allows a reviewer to run a lightweight check without recreating Project 0. It does **not** regenerate the full formula engine, WOE/IV tables, validation windows, stress testing or Power BI pack.

## Headline Sample Checks

- Sample rows: **100,000**
- Matured rows in sample: **95,873**
- Observed default rate: **19.12%**
- Average formula PD: **20.05%**
- EAD proxy: **1,441,666,950**
- Expected loss: **113,513,808**

## Reviewer Quick Run

```bash
python scripts/06_quick_review_from_sample.py
python scripts/02_validate_project3_outputs.py
```

## Full Rebuild

Full rebuild requires the Project 0 data core and public raw datasets documented in `DATA_ACCESS.md`.

## Risk Grade Summary

| risk_grade | policy_action | accounts | observed_default_rate | avg_pd | ead_proxy | expected_loss | el_rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A - Low | Auto approve | 10057 | 0.079248 | 0.085232 | 161042650 | 4116707.335943 | 0.025563 |
| B - Moderate | Approve standard | 20055 | 0.128945 | 0.138738 | 319994375 | 15736271.436768 | 0.049177 |
| C - Watch | Approve with limit/pricing control | 20007 | 0.179587 | 0.183426 | 286022625 | 20075120.583475 | 0.070187 |
| D - High | Manual review | 29980 | 0.216311 | 0.225115 | 412289650 | 39128319.901519 | 0.094905 |
| E - Very High | Decline or require mitigants | 19901 | 0.284408 | 0.301054 | 262317650 | 34457388.733530 | 0.131357 |