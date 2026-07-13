# Publish Steps

## 1. Reviewer Quick-Run

Run this from the public package or GitHub checkout. It does not require Project 0:

```bash
python scripts/06_quick_review_from_sample.py
python scripts/02_validate_project3_outputs.py
```

Expected result:

```text
status: pass
```

## 2. Author Full Rebuild

Full rebuild requires the Project 0 data core and `FINANCIAL_RISK_DATA_CORE`.

```bash
set FINANCIAL_RISK_DATA_CORE=<path_to_project0_data_core>
python scripts/01_build_formula_first_engine.py
python scripts/03_build_completion_pack.py
python scripts/04_build_financial_modeling_summary.py
python scripts/08_build_enriched_scorecard_challenger.py
python scripts/06_quick_review_from_sample.py
python scripts/02_validate_project3_outputs.py
```

## 3. Review Files Before Commit

Include:

- `README.md`
- `DATA_ACCESS.md`
- `ARTIFACT_INDEX.md`
- `requirements.txt`
- `scripts/`
- `docs/`
- `reports/`
- `visuals/`
- `excel/`
- `powerbi/`
- `sql/`
- `github/`
- `website/`

Exclude:

- Raw data
- Large ZIP files
- `.pbix` files
- Credentials
- Private resume/contact details

## 4. Initialize Repo

```bash
git init
git add .
git commit -m "Build credit risk scorecard portfolio analytics"
```

## 5. Create GitHub Repo

Suggested repo name:

```text
credit-risk-scorecard-portfolio-analytics
```

Suggested description:

```text
Formula-first credit risk scorecard and portfolio analytics project covering WOE/IV, PD bands, scorecard points, cutoff strategy, expected loss, enriched challenger benchmarking, validation, monitoring and governance.
```

## 6. Push

```bash
git branch -M main
git remote add origin https://github.com/<your-username>/credit-risk-scorecard-portfolio-analytics.git
git push -u origin main
```

## 7. Pin On GitHub

Pin this repository with the portfolio website and the Project 0 data core.

## 8. Website Update

After GitHub is live, replace local file links in the website with GitHub URLs where appropriate.
