# Implementation Notes - Save Ephesus Elementary Report

This document captures the implementation details, research findings, and verification status for the Save Ephesus Elementary persuasive report.

---

## Section 0: Visual Restyling (January 2026)

### Color Palette: Blue → Red Branding

Adopted the Ephesus Elementary school website color palette (bold red) to replace the original blue academic theme.

| Role | Old | New |
|------|-----|-----|
| Primary (headings, stat-boxes, table headers, callout borders) | `#2E86AB` | `#e6031b` |
| Secondary accent (h3) | `#A23B72` | `#b8020f` |
| Callout/highlight background | `#f0f7fa` / `#e3f2fd` | `#fef9f9` / `#fef0f0` |
| Recommendation border/bg | `#4CAF50` / `#e8f5e9` | `#e6031b` / `#fef9f9` |
| Recommendation h3 | `#2E7D32` | `#b8020f` |
| Highlight class bg | `#fff3cd` | `#fce4e4` |
| Chart: MARKET_COLOR | `#A23B72` | `#666666` |
| Semantic colors (verified green, warning orange, not-met red) | unchanged | unchanged |

### Font Change

- CSS: `Georgia, serif` → `'Segoe UI', Tahoma, Geneva, Verdana, sans-serif`
- Matplotlib: Added `plt.rcParams['font.family'] = 'sans-serif'` with Segoe UI / Tahoma / DejaVu Sans

### CSS Tweaks

| Property | Old | New |
|----------|-----|-----|
| `body line-height` | 1.5 | 1.7 |
| `h2 border-bottom` | 1px solid #ddd | 2px solid #e6031b |
| `.stat-box border-radius` | 5px | 12px |
| `.stat-box` | — | `box-shadow: 0 2px 8px rgba(230,3,27,0.15)` |
| `.callout` | — | `border-radius: 8px` |
| `.recommendation border-radius` | 5px | 12px |
| `.recommendation` | — | `box-shadow: 0 2px 8px rgba(230,3,27,0.1)` |

### School Logo

Added `assets/logos/ephesus-logo.png` (red roadrunner mascot) centered below the h1 title on the first page.

### Files Modified

| File | Changes |
|------|---------|
| `src/visualizations.py` | Color constants updated; font rcParams added |
| `src/report_generator.py` | CSS colors/font/spacing; logo image; inline highlight row colors |
| `templates/report_template.html` | Same CSS/inline updates; logo image |

---

## Section 1: Changelog (January 2026 Updates)

### Removals

**"Small school advantage" claim:**
- Removed from report (was counterproductive - small school size is the primary reason for closure consideration)

**"Gifted programs" claim:**
- Removed (Ephesus does NOT have the LEAP gifted program)

### Reframing

**"Real Cost Question" section:**
- Changed from attacking bond schools to collaborative framing
- Now requests comprehensive analysis of ALL schools, not pitting schools against each other

**"Request for the Board":**
- Made more concise (removed waffly language)
- New text: "We request a comprehensive review of all schools—considering facility condition, walkability, enrollment trends, equity, and housing development—before making closure decisions."

### New Content Sections Added

1. **"The Real Challenge: Attracting Families"** - Explains underlying enrollment problem (housing costs, families choosing other districts)
2. **Enrollment Projections** - Shows Ephesus projected to GROW (+21 by 2036)
3. **Transportation Crisis** - CHCCS bus driver shortage data
4. **Equity and Achievement Gaps** - Stanford data on Chapel Hill racial disparities
5. **Research on School Closure Impacts** - Academic citations from peer-reviewed research

### Table/Figure Updates

| Item | Change |
|------|--------|
| Table 1 (Academic Growth) | Expanded from top 5 to ALL 11 schools |
| Figure 2 (Demographics) | Fixed Ephesus color scheme (was two blue bars, now matches others with blue FRL + purple minority); highlighted with gold border |
| Figure 3 (Ephesus Housing) | Combined Greenfield Place + Commons; added dashed bar for Longleaf Trace (150 planned units) |
| Figure 4 (District Housing) | Added dashed bar for Longleaf Trace (150 units) in Ephesus zone |
| Figure 5 (20-Year Cost) | REMOVED entirely (not needed) |

### Citation System Updates

- Replaced inline "NCES Verified" text with superscript numbers
- Replaced "Data Integrity Statement" with numbered References section (14 sources)

---

## Section 2: Research Findings

### NC Bus Driver Shortage (CHCCS-Specific)

| Metric | Value | Source |
|--------|-------|--------|
| Driver count decline | 70+ → 37 drivers | Chapelboro |
| Instructional hours lost | 3,950 (first 39 days, 2023-24) | WRAL |
| NC national ranking (pay) | 50th | NC State Board of Education |
| Average driver salary | $14,628/year | NC State Board of Education |
| States paying 50%+ more | 27 states | NC State Board of Education |

**Implication:** Adding bus routes for 99 former walkers creates operational risk when the district cannot adequately staff existing routes.

### Racial Disparity in Chapel Hill

| Metric | Value | Source |
|--------|-------|--------|
| Black students achievement gap | 4.3 grade levels behind white peers | Stanford Educational Opportunity Project |
| AP class enrollment disparity | Black students 3.7x less likely to enroll | NC Report Cards |
| Discipline disparity | 45% of suspensions (11.4% of enrollment) | NC Report Cards |

**Why it matters:** Closing a Title I school serving diverse, low-income populations may exacerbate existing inequities.

### Academic Research on School Closure Impacts

| Citation | Key Finding |
|----------|-------------|
| Engberg et al. (2012) | Closures disproportionately affect low-income students |
| Sunderman & Payne (2009) | Students from closed schools show academic decline |
| de la Torre & Gwynne (2009) | Displaced students rarely land in higher-performing schools |
| Kirshner et al. (2010) | Closure creates emotional and academic disruption |

### Longleaf Trace Housing Development (Updated)

| Field | Value |
|-------|-------|
| Project Name | Longleaf Trace |
| Location | 1714 Legion Road (36.2 acres) |
| Units | **150 affordable units** |
| Type | 100% affordable (LIHTC) |
| Status | LIHTC awarded Aug 2024; construction ~2027-2029 |
| School Zone | Ephesus (adjacent to Ephesus Park) |

**Primary Source:** https://www.chapelhillaffordablehousing.org/legion-road

**Additional Sources:**
- Chapel Hill Engage: https://engage.chapelhillnc.gov/legion-property
- Chapelboro: https://chapelboro.com/news/local-government/chapel-hill-shares-latest-pond-removal-construction-timeline-for-legion-road-housing-and-park-project
- Daily Tar Heel: https://www.dailytarheel.com/article/2024/09/city-longleaf-trace-tax-credit-award-chapel-hill-affordable-housing

---

## Section 3: Full References

1. **NCES Common Core of Data** - https://nces.ed.gov/ccd/schoolsearch/
2. **NC School Report Cards (2023-24)** - https://ncreports.ondemand.sas.com/
3. **Town of Chapel Hill** - https://www.townofchapelhill.org/
4. **Chapel Hill Affordable Housing** - https://www.chapelhillaffordablehousing.org/
5. **CHCCS Bond Overview** - https://www.chccs.org/community/schoolbond/overview
6. **Chapelboro News** - https://chapelboro.com/
7. **Stanford Educational Opportunity Project** - https://edopportunity.org/
8. **WRAL News** - https://www.wral.com/
9. **Daily Tar Heel** - https://www.dailytarheel.com/
10. **Engberg et al. (2012)** - RAND Corporation
11. **de la Torre & Gwynne (2009)** - UChicago Consortium on School Research
12. **Kirshner et al. (2010)** - Teachers College Record
13. **Legion Road Housing** - https://www.chapelhillaffordablehousing.org/legion-road
14. **CHCCS Enrollment Projections** - Slide 28 (district presentation)

---

## Section 4: Verification Checklist

### Content Fixes (All Complete)

- [x] "Small school advantage" removed
- [x] "Gifted programs" removed
- [x] Cost question reframed (collaborative, not attacking)
- [x] Underlying problem section added
- [x] Enrollment comparison included
- [x] Bus driver shortage section added
- [x] Racial disparity section added
- [x] Academic research citations added

### Table/Figure Updates (All Complete)

- [x] Table 1 expanded to all 11 schools
- [x] Figure 2 fixed (same colors for all schools, Ephesus highlighted with gold)
- [x] Figure 3 updated (combined Greenfield + Longleaf Trace 150 units dashed)
- [x] Figure 4 updated (Longleaf Trace 150 units dashed bar added)
- [x] Figure 5 removed (was 20-year cost analysis)

### Citation/Reference Updates (All Complete)

- [x] Data Integrity replaced with References section
- [x] Superscript citations added throughout

### Regeneration Status

- [x] Visualizations updated (`src/visualizations.py`)
- [x] Report updated (`src/report_generator.py`)
- [x] Charts regenerated (run `python src/visualizations.py`)
- [x] Report HTML regenerated (run `python src/report_generator.py`)

---

## Section 5: Commands to Regenerate

```bash
# Generate updated visualizations
python src/visualizations.py

# Generate updated report (HTML + PDF if WeasyPrint available)
python src/report_generator.py
```

**Note:** If WeasyPrint is not installed, the HTML template will be generated. Open in a browser and use Print > Save as PDF.

---

## Section 6: File Modification Summary

| File | Changes Made |
|------|-------------|
| `src/visualizations.py` | Fixed demographics chart colors; updated Longleaf Trace to 150 units; removed keep_vs_close chart; red branding + sans-serif font |
| `src/report_generator.py` | Updated housing table (150 units); removed Figure 5; made "Request for the Board" concise; red branding + logo + sans-serif font |
| `templates/report_template.html` | Red branding + logo + sans-serif font (matches report_generator.py) |
| `docs/key_messages.md` | Updated Request for the Board (concise version) |
| `docs/IMPLEMENTATION_NOTES.md` | Created (this file) |
| `CLAUDE.md` | Updated file structure section |

---

---

## Attribution

This report was developed with assistance from Claude (Anthropic) for data organization, visualization code, and document drafting. All claims have been independently verified against official sources.

---

*Last updated: January 2026*
