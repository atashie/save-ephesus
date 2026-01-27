# Don't Close Ephesus Elementary

<p align="center">
  <img src="assets/logos/ephesus-logo.png" alt="Ephesus Elementary Roadrunner" height="140">
</p>

A data-driven report to the **Chapel Hill-Carrboro City Schools (CHCCS) Board of Education** making the case for keeping Ephesus Elementary School open.

---

## Key Arguments

| # | Argument | Headline Stat |
|---|----------|---------------|
| 1 | **Walkable Community School** | 99 students walk to school |
| 2 | **Academic Excellence** | #4 of 11 in growth (85.8, "Exceeded") |
| 3 | **Housing Development** | 713 units nearby (563 built + 150 planned) |
| 4 | **Equity** | Title I school, 30-36% FRL, 50% minority |

## Generating the Report

**Prerequisites:** Python 3.9+, plus the packages in `requirements.txt`.

```bash
pip install -r requirements.txt
```

**Generate charts and HTML report:**

```bash
python src/visualizations.py      # outputs to assets/charts/
python src/report_generator.py    # outputs to templates/report_template.html
```

Open `templates/report_template.html` in a browser and **Print > Save as PDF** for the final output. (WeasyPrint PDF generation is supported if installed, but optional.)

## Repository Structure

```
save_ephesus/
├── README.md
├── CLAUDE.md                    # Project guide & AI instructions
├── requirements.txt
├── src/
│   ├── visualizations.py        # Matplotlib chart generation
│   └── report_generator.py      # HTML/PDF report assembly
├── assets/
│   ├── charts/                  # Generated chart PNGs
│   └── logos/                   # School logo
├── templates/
│   └── report_template.html     # Final report (open in browser)
├── output/                      # PDF output (if WeasyPrint available)
└── docs/
    ├── RESEARCH_DATA.md         # Detailed data tables & sources
    ├── IMPLEMENTATION_NOTES.md  # Changelog & verification status
    ├── key_messages.md          # Talking points & sound bites
    └── executive_summary.md     # One-page summary
```

## Data Sources

All claims are backed by verified, publicly available data:

- **NC School Report Cards** (2023-24) -- academic growth scores
- **NCES Common Core of Data** -- demographics and Title I status
- **Town of Chapel Hill** -- housing development records
- **Chapel Hill Affordable Housing** -- Longleaf Trace, Greenfield projects
- **CHCCS** -- budget, bond, and enrollment data

See [`docs/RESEARCH_DATA.md`](docs/RESEARCH_DATA.md) for full data tables and source links.

## Intellectual Honesty

This report follows strict honesty standards:

- No fabricated data -- every claim has a source
- Counterarguments acknowledged (e.g., Morris Grove has ~2x Ephesus's housing development)
- Parent-supplied figures marked with `*`
- Unverified estimates clearly labeled

## License

This material is provided for community advocacy purposes. Data sourced from public records.
