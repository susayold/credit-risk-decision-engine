# Power BI Build Steps

1. Open Power BI Desktop.
2. Import CSV files from the `reports/` folder, especially reports `03`, `05`-`11`, and `16`-`29`.
3. Rename tables according to `data_model.md`.
4. Create DAX measures from `dax_measures.md`.
5. Build pages using `page_layout_spec.md`.
6. Use `visual_mapping.csv` to confirm field/measure placement.
7. Export screenshots for the portfolio website after visual review.

Important: Power BI is the presentation layer. The formulas should remain reproducible in `scripts/01_build_formula_first_engine.py` and `scripts/03_build_completion_pack.py`.
