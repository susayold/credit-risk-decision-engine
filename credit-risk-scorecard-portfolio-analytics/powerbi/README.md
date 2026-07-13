# Power BI Pack

This folder defines the Power BI build standard for Project 3.

The `.pbix` file is not generated here. The final dashboard should be built manually in Power BI Desktop using the report outputs created by:

`scripts/01_build_formula_first_engine.py`

and extended by:

`scripts/03_build_completion_pack.py`

## Files

- `data_model.md`: tables, grain and relationship guidance
- `dax_measures.md`: measures for score bands, validation, cutoff, expected loss, monitoring, stress, pricing, concentration and tests
- `page_layout_spec.md`: dashboard pages and visual purposes
- `visual_mapping.csv`: field-to-visual mapping
- `build_steps.md`: build workflow
- `theme.json`: portfolio theme

## Recommended Pages

1. Executive Summary
2. Risk Grade Performance
3. Cutoff Strategy
4. Validation And Calibration
5. Vintage And Monitoring
6. ECL And Stress Testing
7. Pricing And Concentration
8. Governance And Test Evidence
