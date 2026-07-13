-- Project 3: Credit Risk Scorecard & Portfolio Analytics
-- SQL risk KPI query pack
-- Dialect: DuckDB-style SQL over CSV exports.

-- 01. Population and target summary
SELECT
  COUNT(*) AS accounts,
  SUM(CASE WHEN matured_flag = 1 THEN 1 ELSE 0 END) AS matured_accounts,
  SUM(CASE WHEN monitor_only_flag = 1 THEN 1 ELSE 0 END) AS monitor_only_accounts,
  AVG(CASE WHEN matured_flag = 1 THEN bad_flag END) AS matured_default_rate
FROM read_csv_auto('data/processed/formula_engine_account_sample.csv.gz');

-- 02. Risk grade performance
SELECT
  risk_grade,
  policy_action,
  COUNT(*) AS accounts,
  AVG(bad_flag) AS observed_default_rate,
  AVG(pd_formula) AS avg_pd,
  AVG(scorecard_points) AS avg_score,
  SUM(ead_proxy) AS ead_proxy,
  SUM(expected_loss_formula) AS expected_loss,
  SUM(expected_loss_formula) / NULLIF(SUM(ead_proxy), 0) AS el_rate
FROM read_csv_auto('data/processed/formula_engine_account_sample.csv.gz')
WHERE matured_flag = 1
GROUP BY risk_grade, policy_action
ORDER BY avg_pd;

-- 03. Expected loss by policy action
SELECT
  policy_action,
  COUNT(*) AS accounts,
  SUM(ead_proxy) AS ead_proxy,
  SUM(expected_loss_formula) AS expected_loss,
  SUM(expected_loss_formula) / NULLIF(SUM(ead_proxy), 0) AS el_rate
FROM read_csv_auto('data/processed/formula_engine_account_sample.csv.gz')
GROUP BY policy_action
ORDER BY expected_loss DESC;

-- 04. Monthly cohort monitoring
SELECT
  DATE_TRUNC('month', application_month) AS application_month,
  COUNT(*) AS accounts,
  AVG(pd_formula) AS avg_pd,
  AVG(CASE WHEN matured_flag = 1 THEN bad_flag END) AS observed_default_rate,
  SUM(expected_loss_formula) AS expected_loss
FROM read_csv_auto('data/processed/formula_engine_account_sample.csv.gz')
GROUP BY 1
ORDER BY 1;

-- 05. Cutoff strategy output
SELECT *
FROM read_csv_auto('reports/08_cutoff_strategy.csv')
ORDER BY pd_cutoff;

-- 06. Validation metrics output
SELECT *
FROM read_csv_auto('reports/06_validation_metrics.csv')
ORDER BY sample;

-- 07. Vintage monitoring output
SELECT
  vintage_quarter,
  vintage_month,
  accounts,
  matured_accounts,
  bad_accounts,
  vintage_bad_rate,
  avg_pd,
  expected_loss,
  el_rate
FROM read_csv_auto('reports/19_vintage_analysis.csv')
ORDER BY vintage_month;

-- 08. IFRS 9 ECL bridge
SELECT
  stage,
  fico_band,
  accounts,
  ead,
  avg_pd,
  avg_lgd,
  ecl_12m_or_base,
  ecl_lifetime_proxy,
  ecl_rate_base,
  ecl_rate_lifetime_proxy
FROM read_csv_auto('reports/21_ifrs9_ecl_bridge.csv')
ORDER BY stage, fico_band;

-- 09. Stress testing scenario summary
SELECT
  scenario,
  SUM(accounts) AS accounts,
  SUM(stressed_ead) AS stressed_ead,
  SUM(stressed_el) AS stressed_expected_loss,
  SUM(stressed_el) / NULLIF(SUM(stressed_ead), 0) AS stressed_el_rate
FROM read_csv_auto('reports/22_stress_testing_scenarios.csv')
GROUP BY scenario
ORDER BY
  CASE scenario
    WHEN 'Base' THEN 1
    WHEN 'Mild Downturn' THEN 2
    WHEN 'Adverse' THEN 3
    WHEN 'Severe' THEN 4
    ELSE 99
  END;

-- 10. Risk-based pricing by grade
SELECT
  risk_grade,
  policy_action,
  el_rate,
  funding_cost_rate,
  operating_cost_rate,
  capital_cost_rate,
  profit_margin_rate,
  required_rate,
  illustrative_offered_rate,
  raroc_proxy
FROM read_csv_auto('reports/23_risk_based_pricing_by_grade.csv')
ORDER BY required_rate;

-- 11. Top expected-loss concentration segments
SELECT
  segment_variable,
  segment_value,
  accounts,
  ead,
  expected_loss,
  ead_share,
  el_share,
  concentration_flag
FROM read_csv_auto('reports/25_concentration_risk_by_segment.csv')
ORDER BY expected_loss DESC
LIMIT 25;

-- 12. Formula test evidence
SELECT
  test_id,
  test_name,
  status,
  evidence
FROM read_csv_auto('reports/29_formula_test_cases.csv')
ORDER BY test_id;
