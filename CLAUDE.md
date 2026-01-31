# Save Ephesus Elementary - Project Guide

## Project Overview
Persuasive PDF report for the CHCCS Board of Education arguing for keeping Ephesus Elementary School open. Report is complete and generated.

## CRITICAL: Intellectual Honesty Requirements

**This report's credibility depends on absolute honesty:**

1. **NEVER fabricate data** - No source = no claim
2. **NEVER overstate claims** - Be precise about what data shows
3. **Acknowledge counterarguments** - Other schools have strengths too
4. **Mark unverified claims** - Use `*` for parent-supplied data
5. **Be transparent about limitations** - Say when data is incomplete

| Symbol | Meaning |
|--------|---------|
| ✓ | Verified with official source |
| * | Parent-supplied, needs verification |

---

## Key Arguments (Summary)

### 1. Walkable Community School
- **#1 most walkable** elementary school in district ✓
- 99 students within 0.5 miles (24.7% of enrollment) ✓
- Closing = more buses (~$66K/year added cost)

### 2. Academic Excellence
- **#4 of 11** in academic growth (85.8, "Exceeded" status) ✓
- Title I school achieving exceptional results

### 3. Housing Development
- **713 total units** near Ephesus (563 built + 150 planned)
- 299 affordable units (42% of total)
- Longleaf Trace: 150 affordable units planned 2027-29

### 4. Equity
- **Title I school** (federally designated high-poverty) ✓
- 30-36% free/reduced lunch ✓
- 50% minority enrollment ✓

### 5. Teacher Survey Results (NC TWC Survey 2024) ✓
- **97.67%** of teachers say students follow conduct rules (+29 pts vs district) ✓
- **Zero incidents** of violence threats, cyberbullying, weapons, drugs ✓
- Physical conflicts **5x lower** than district average (7% vs 36%) ✓
- **97.67%** say it's a good place to work (+6 pts vs district) ✓
- **97.67%** say parents know what's going on (+13 pts vs district) ✓

> **See `docs/RESEARCH_DATA.md` for detailed data tables and sources.**
>
> **See `data/processed/teacher_survey_analysis.md` for full teacher survey analysis.**
>
> **See `data/processed/bond_presentation_2024.md` for district decision-making framework and evaluation criteria.**
>
> **See `data/processed/safe_routes_analysis.md` for walkability data and infrastructure plans.**
>
> **See `data/processed/enrollment_history.csv` for 35-year enrollment data (1990-2024) for all 11 schools, with sources in `enrollment_history_sources.md`.**

---

## Verified Summary Data

| Metric | Value | Status |
|--------|-------|--------|
| Academic growth rank | #4 of 11 | ✓ Verified |
| Growth score | 85.8 ("Exceeded") | ✓ Verified |
| Housing units (built) | 563 | ✓ Verified |
| Housing units (planned) | 150 (Longleaf Trace) | ✓ Verified |
| Affordable units | 299 total (149 built + 150 planned) | ✓ Verified |
| Closure savings | ~$1.7M/year | ✓ Verified |
| Net savings after costs | ~$1.53M/year | ✓ Calculated |
| Renovation estimate | $28.9M (Woolpert) | ✓ Verified |
| Students follow conduct rules | 97.67% (+29 pts vs district) | ✓ NC TWC Survey 2024 |
| Physical conflicts rate | 6.98% (5x lower than district) | ✓ NC TWC Survey 2024 |
| Teacher satisfaction | 97.67% "good place to work" | ✓ NC TWC Survey 2024 |
| Walkability rank | #1 (24.7% within 0.5 mi) | ✓ Safe Routes 2025 |

---

## File Structure

```
save_ephesus/
├── CLAUDE.md                    # This file - project guide
├── requirements.txt
├── src/
│   ├── visualizations.py        # Chart generation
│   └── report_generator.py      # HTML/PDF report
├── assets/charts/               # Generated charts
├── assets/logos/                # School logo (ephesus-logo.png)
├── templates/
│   └── report_template.html     # Final report HTML
├── output/
│   └── ephesus_report.pdf
├── data/
│   ├── raw/
│   │   └── teacher_surveys/          # NC TWC Survey 2024 CSV files
│   └── processed/
│       ├── bond_presentation_2024.md  # Bond decision framework
│       ├── teacher_survey_analysis.md # Teacher survey findings
│       ├── enrollment_history.csv     # 35-year enrollment (1990-2024)
│       └── enrollment_history_sources.md # Data sources for enrollment
└── docs/
    ├── key_messages.md          # Talking points and sound bites
    ├── RESEARCH_DATA.md         # Detailed data tables and sources
    ├── IMPLEMENTATION_NOTES.md  # Changelog and verification status
    └── executive_summary.md
```

---

## Commands

```bash
# Generate visualizations
python src/visualizations.py

# Generate report (HTML; print to PDF from browser)
python src/report_generator.py
```

---

## Key Contacts
- CHCCS Communications: communications@chccs.org
- Town of Chapel Hill Planning: planning@townofchapelhill.org
- NC DPI Data Request: accountability@dpi.nc.gov
