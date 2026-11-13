# Clark Visitor Intelligence Lab

A local Streamlit prototype for profiling and cleaning Leadfeeder Excel exports before ML experimentation.

## Start

```bash
python -m venv .venv
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Upload the original Leadfeeder Excel workbook (sheet `Leadfeeder Visits`). The application validates required columns, preserves raw data, flags duplicates and invalid fields, normalizes timestamps, and creates company-level behavioral features. Download cleaned pageviews or company features as CSV.

## Methodology

- Each input row is a pageview, **not** a visit or a person.
- Visits are distinct `Visit ID`; companies are distinct `Company ID`.
- Territory uses **Visit region**, not the company headquarters `Region`.
- Exact duplicates are **flagged**, not removed: identical rows may be legitimate repeated pageviews in this export.
- Page classification is URL-pattern-based and must be reviewed against Clark's site taxonomy.
- Missing time-on-page is not imputed to zero; zero durations may be measurement artifacts.
- No clustering or predictive probabilities are claimed yet.
- Avoid hosting publicly with customer data; add access control and data retention policy before production.

## Next experiment

Audit feature distributions and outliers, then evaluate whether a meaningful segmentation exists; collect longer history before treating clusters as stable.
