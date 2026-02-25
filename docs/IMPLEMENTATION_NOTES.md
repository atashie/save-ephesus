# Implementation Notes - Save Ephesus Elementary Report

This document captures the implementation details, research findings, and verification status for the Save Ephesus Elementary persuasive report.

---

## Flood Plain Analysis (February 2026)

### Overview

Added FEMA flood plain overlay on school property parcels to show FPG has the most significant flood exposure of any CHCCS elementary school.

### Key Findings

| School | 100-yr Overlap | % of Property |
|--------|---------------|---------------|
| FPG Bilingue | 2.59 acres | 26% of 9.8 ac |
| Rashkis | 1.22 acres | 7% of 17.14 ac |
| All others | 0 | 0% |

### Data Sources

- **Flood zones:** FEMA National Flood Hazard Layer (NFHL), layer 28 (S_FLD_HAZ_AR), queried via ArcGIS REST API with 3x3 tiled bbox requests
- **School properties:** Orange County parcel data (`combined_data_polys.gpkg`), matched by which parcel contains each school's NCES coordinate point
- **School locations:** `data/cache/nces_school_locations.csv` (NCES EDGE 2023-24)

### Files Created

| File | Purpose |
|------|---------|
| `src/flood_map.py` | Standalone script: downloads FEMA data, identifies school parcels, computes overlaps, renders two-panel PNG |
| `assets/maps/flood_school_properties.png` | Two-panel map: district overview + FPG zoom detail |
| `data/cache/fema_flood_zones.gpkg` | Cached FEMA flood zone polygons (1,123 features) |

### Files Modified

| File | Changes |
|------|---------|
| `CLAUDE.md` | Added flood_map.py to file structure and commands |
| `docs/RESEARCH_DATA.md` | Added Flood Plain Data section with overlap table |
| `docs/IMPLEMENTATION_NOTES.md` | This section |

### Technical Notes

- FEMA API (`hazards.fema.gov/arcgis/...`) errors on large bounding boxes; solved by tiling into 3x3 sub-bboxes
- Some FEMA polygons have invalid geometry; fixed with `make_valid()` before `unary_union`
- School parcels are owned by various entities (school board, Orange County, Town of Chapel Hill); identified by spatial containment of NCES point rather than owner name filtering

---

## Section 0: Teacher Survey Integration (January 2026)

### Overview

Integrated NC Teacher Working Conditions Survey 2024 data to strengthen the case with verified teacher feedback.

### Key Findings Added

| Metric | Ephesus | District | Difference |
|--------|---------|----------|------------|
| Students follow conduct rules | 97.67% | 68.83% | +29 pts |
| Physical conflicts | 6.98% | 36.38% | 5x fewer |
| Violence threats | 0% | 15.54% | Zero |
| Cyberbullying | 0% | 27.43% | Zero |
| Weapons possession | 0% | 9.05% | Zero |
| Drug/tobacco use | 0% | 28.42% | Zero |
| Good place to work | 97.67% | 91.25% | +6 pts |
| Parents know what's going on | 97.67% | 84.86% | +13 pts |

### Files Created

| File | Purpose |
|------|---------|
| `data/processed/teacher_survey_analysis.md` | Full analysis document with all metrics |
| `assets/charts/teacher_survey_conduct.png` | Bar chart: conduct metrics comparison |
| `assets/charts/teacher_survey_problems.png` | Bar chart: behavioral problems (lower=better) |
| `assets/charts/teacher_survey_community.png` | Bar chart: community engagement |

### Files Modified

| File | Changes |
|------|---------|
| `src/visualizations.py` | Added 3 new chart functions for teacher survey data |
| `src/report_generator.py` | Added "School Climate & Safety" section; updated exec summary; added reference #16 |
| `CLAUDE.md` | Added teacher survey to Key Arguments and Verified Summary Data |
| `docs/RESEARCH_DATA.md` | Added full Teacher Survey Data section with tables |
| `docs/key_messages.md` | Added School Climate message with sound bites |
| `docs/executive_summary.md` | Added Key Statistics and School Climate section |

### Report Changes

1. **Executive Summary stat boxes**: Updated to show conduct (+29 pts) and zero violence
2. **Executive Summary bullets**: Added "exceptional school climate" point
3. **"What Makes Ephesus Successful"**: Now data-backed with survey citations
4. **NEW Section**: "School Climate & Safety" page with chart and table
5. **Community Impact**: Added parent engagement data (+13 pts)
6. **References**: Added #16 for NC TWC Survey 2024

### Source Data

- Raw CSV files: `data/raw/teacher_surveys/ephesus_elementary_*.csv`
- District comparison: `data/raw/teacher_surveys/chccs_district_*.csv`
- Survey website: https://nctwcs.org/

---

## Section 0b: Visual Restyling (January 2026)

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

### District Decision Framework (2024 Bond Presentation)

The 2024 Bond Presentation establishes the official evaluation criteria used for facility decisions.

| Criterion | Relevance to Ephesus |
|-----------|---------------------|
| Walkability impact | Explicit evaluation metric (Maintained/Reduced/Not available) |
| Transportation impact | Bus routes, ride time, traffic - all worsen with closure |
| Student displacement | Ephesus (~390-410 students) = Yellow category (200-450) |
| Community values | Slide 15: "Maintain walkability and minimize disruption" |

**Source:** `data/processed/bond_presentation_2024.md`

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
| `data/processed/bond_presentation_2024.md` | Processed bond presentation data; district decision framework |

---

---

## Section 7: Safe Routes Integration (January 2026)

### Key Data Integrated from Safe Routes to School Action Plan

| Finding | Value | Source |
|---------|-------|--------|
| Walkability rank | #1 in district | Safe Routes Action Plan |
| Students within 0.5 mi | 99 (24.7%) | Town of Chapel Hill GIS, Feb 2025 |
| Active transportation rate | 78 students (20%) | Field tally, Nov 2024 |
| Households without vehicles | 1,100+ | 2023 Census |
| Distance as barrier | 66% cite as #1 | 2024 Intent Survey (5,524 families) |
| Town infrastructure projects | 12 planned | Safe Routes Action Plan |

### Report Template Changes

- Executive Summary: Added "#1 Most Walkable" stat box
- Executive Summary: Updated "99" stat (removed asterisk, now verified)
- Walkability section: Added #1 ranking callout, comparison table, equity context
- Equity section: Added new demographics (14.7% SWD, 13% ML, 35.8% SED)
- Transportation section: Added Vision Zero context, survey findings
- References: Added Safe Routes to School Action Plan (ref #17)

### Walkability Data Status Change

| Before | After |
|--------|-------|
| 99* (parent-reported) | 99 ✓ (verified by Town of Chapel Hill GIS, Feb 2025) |

---

## Section 8: School Desert Analysis (February 2026)

### Overview

Interactive map (`school_community_map.html`) showing travel-time impacts of closing each elementary school, with affected-household histograms that update per scenario and travel mode.

### Workflow

1. **Load schools** — NCES EDGE 2023-24 locations (11 schools, cached at `data/cache/nces_school_locations.csv`)
2. **Load district boundary** — Census TIGER/Line GEOID 3700720 (cached as GeoPackage)
3. **Download road networks** — OSMnx drive/bike/walk graphs, cached as GraphML; reverse edges added for bidirectional traversal
4. **Dijkstra from each school** — 33 runs (11 schools × 3 modes), each exploring the full graph (no cutoff)
5. **Create grid** — 100 m resolution point grid inside district polygon (~16K points); school locations injected as zero-time anchor points
6. **Edge-snap grid points** — Each grid point snaps to the nearest road edge via Shapely STRtree (not just nearest node); travel time is interpolated along the matched edge using fractional position; off-network access leg adds time at a mode-specific fraction of modal speed (walk 90%, bike 80%, drive 20%)
7. **Compute desert scores** — For each grid point × scenario × mode, take min travel time across open schools; delta = scenario time − baseline time
8. **Rasterize** — Grid values projected onto a shared pixel grid (WGS84), gap-filled for UTM→WGS84 rotation artifacts, masked to district polygon; colorized with RdYlGn_r (absolute) or Oranges (delta); saved as GeoTIFF + base64 PNG for Leaflet image overlays
9. **Load property centroids** — ~21K residential parcels from Orange County GIS (`combined_data_centroids.gpkg`), clipped to district boundary
10. **Snap centroids to grid** — cKDTree with cos(lat) longitude scaling; each parcel assigned its nearest `grid_id`
11. **Compute affected parcels** — For each non-baseline scenario × mode, parcels whose grid point has `delta_minutes > 0` are "affected"
12. **Render histograms** — Two matplotlib charts per scenario|mode: assessed value (blue, 25 bins) and years since sale (green, 25 bins), each with a red dashed median line; encoded as base64 PNGs
13. **Build map** — Folium map with all overlays + JS switching; chart panel occupies bottom 35vh of viewport and updates on scenario/mode change

### Definition of "Affected"

A residential parcel is **affected** if its nearest grid point has `delta_minutes > 0` for the selected closure scenario + travel mode. This means closing that school increased travel time to the nearest remaining school at that location.

### Assumptions

| Assumption | Rationale |
|-----------|-----------|
| Static travel speeds (no real-time traffic, no turn penalties) | Consistent, reproducible model; effective speeds already discount for signals/stops via HCM6 ratios |
| Walk speed 2.5 mph for all K-5 | Mid-range of MUTCD/FHWA measurements for school-age children |
| Effective drive speeds 65-92% of posted | HCM6 Ch.16 and FHWA Urban Arterial Speed Studies |
| Off-network access leg at reduced speed (walk 90%, bike 80%, drive 20%) | Walking/biking to the road is nearly full-speed; driving off-network (driveways, lots) is much slower |
| Grid points >200 m from any road are unreachable | 2× grid resolution; filters lakes, large parks, undeveloped land |
| All remaining schools absorb displaced students | No capacity constraints modeled |
| Binary affected definition (delta > 0) | Simple, transparent; does not weight by magnitude of increase |
| Parcel-to-grid snapping uses Euclidean nearest point | Not network distance; acceptable at 100 m grid resolution |

### Limitations

- **No capacity constraints:** The model assumes every remaining school can absorb displaced students. In practice, some schools may be full.
- **No turn penalties or intersection delays:** Dijkstra uses edge-level travel times only; left-turn delays, traffic signals, and stop signs are approximated by the effective speed reduction but not modeled explicitly.
- **Tax-record lag:** Assessed values are from the latest Orange County tax records and may not reflect current market values.
- **Sale date coverage:** `years_since_sale` reflects the most recent recorded deed transfer. Properties with no recorded sale are excluded from that histogram (shown as NaN).
- **Static road network:** The OSM snapshot is fixed at download time. Road construction or closures after download are not reflected.
- **No school-choice or magnet effects:** The model assumes families attend their geographically nearest school. Magnet, charter, and school-choice assignments are not modeled.

### Key Outputs

| Output | Description |
|--------|-------------|
| `assets/maps/school_community_map.html` | Interactive map: heatmap + road network + property parcels + affected-household histograms |
| `data/processed/school_desert_grid.csv` | ~340K rows: grid_id × scenario × mode with travel times and deltas |
| `data/cache/school_desert_tiffs/` | GeoTIFF rasters for each scenario/mode/layer |

### Files Modified

| File | Changes |
|------|---------|
| `src/school_desert.py` | `_render_affected_charts()` function; grid-snapping + affected-data computation in `main()`; `affected_charts` parameter threaded through `create_map()` → `_build_control_html()`; CSS/HTML/JS for chart panel below map |

### Affected Household Counts (February 2026 baseline)

| Scenario | Drive | Bike | Walk |
|----------|-------|------|------|
| Close Ephesus | 3,216 | 2,712 | 2,244 |
| Close Glenwood | 838 | 551 | 909 |
| Close FPG | 2,566 | 1,366 | 1,336 |
| Close Estes Hills | 3,144 | 3,412 | 3,914 |
| Close Seawell | 1,914 | 2,431 | 2,139 |
| Close Ephesus + Glenwood | 4,054 | 3,263 | 3,153 |

---

## Section 9: Socioeconomic Analysis (February 2026)

### Overview

Census-based demographic analysis of CHCCS elementary school attendance zones using ACS 5-Year block group estimates and 2020 Decennial block-level race data, with dasymetric areal interpolation weighted by residential parcel area. Produces per-zone demographic summaries, an interactive Folium map, static comparison charts, and auto-generated methodology documentation.

### Key Features

- **7 choropleth layers** (block level): median income, % below 185% poverty, % minority, % renter, % zero-vehicle, % elementary age 5-9, % young children 0-4
- **1:1 dot-density race layer** (~95,764 dots) with dasymetric placement constrained to residential parcels
- **5 zone types** with radio-button switching: School Zones (10 attendance zones), Walk Zones (7 CHCCS walk zones), Nearest Walk (11 Voronoi-like zones), Nearest Bike (11), Nearest Drive (11)
- **Per-zone barplots and histograms** rendered in a sidebar panel, updating on zone type and school selection
- **Batch JS rendering** for dot-density (compact array + for-loop, Canvas renderer)

### Files Created

| File | Purpose |
|------|---------|
| `src/school_socioeconomic_analysis.py` | Main module (~2,860 lines): Census API download, spatial analysis, dasymetric interpolation, dot-density generation, Folium map, charts, auto-docs |
| `SOCIOECONOMIC_ANALYSIS_AND_LIMITATIONS.md` | Methodology documentation with 26 numbered limitations |
| `assets/maps/school_socioeconomic_map.html` | Interactive Folium map with choropleth, dot-density, and 5 zone type overlays |
| `assets/charts/socioeconomic_*.png` | 7 horizontal bar charts + 1 income distribution chart |
| `data/processed/census_school_demographics.csv` | Per-school-zone demographic summaries (10 schools, ~20 metrics) |
| `data/processed/census_blockgroup_profiles.csv` | Block-group-level derived metrics within district |
| `docs/socioeconomic/SOCIOECONOMIC_ANALYSIS.md` | Auto-generated methodology and results documentation |

### Bug Fix: Orphan Brace in JavaScript

Removed an orphan `}}` brace (was at line 2084) left over from removing the "Show Zones" checkbox toggle. This extra brace prematurely closed the `DOMContentLoaded` event listener, which caused:
- Per-zone barplots and histograms to never render (the chart-rendering code was outside the listener scope)
- The map title to fade/disappear (title-injection code was also outside the listener)

### Files Modified

| File | Changes |
|------|---------|
| `CLAUDE.md` | Added socioeconomic analysis to file structure, commands, and cross-references |
| `src/road_pollution.py` | Fixed chart layout (`plt.subplots_adjust` for road pollution comparison chart) |

---

## Attribution

This report was developed with assistance from Claude (Anthropic) for data organization, visualization code, and document drafting. All claims have been independently verified against official sources.

---

*Last updated: February 25, 2026*
