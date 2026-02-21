# Data Sources for Save Ephesus Report

## Official Sources

### Academic Performance
- **NC School Report Cards**
  - URL: https://ncreports.ondemand.sas.com/
  - Data: Academic growth, proficiency rates, school grades
  - Access Date: January 2025
  - Status: ✓ VERIFIED

### Enrollment Data
- **NCES Common Core of Data**
  - URL: https://nces.ed.gov/ccd/schoolsearch/
  - Data: Enrollment, demographics, Title I status
  - Access Date: January 2025
  - Status: ✓ VERIFIED

### District Information
- **CHCCS Official Website**
  - URL: https://www.chccs.org
  - Data: School profiles, capacity, programs
  - Access Date: January 2025
  - Status: ✓ VERIFIED

### Bond Information
- **CHCCS School Bond**
  - URL: https://www.chccs.org/community/schoolbond/overview
  - Data: $300M bond allocation, renovation costs
  - Access Date: January 2025
  - Status: ✓ VERIFIED

### Housing Development
- **Town of Chapel Hill**
  - URL: https://www.townofchapelhill.org
  - Data: Housing projects, development plans
  - Access Date: January 2025
  - Status: ✓ VERIFIED

- **Chapel Hill Affordable Housing**
  - URL: https://www.chapelhillaffordablehousing.org
  - Data: Project details, unit counts
  - Access Date: January 2025
  - Status: ✓ VERIFIED

### Board Meeting Archives
- **CHCCS Granicus Archive**
  - URL: https://chccs.granicus.com/viewpublisher.php?view_id=2
  - Data: Board meeting videos and documents
  - Access Date: January 2025
  - Status: ✓ VERIFIED

### Facility Assessment
- **George Griffin Substack (Board Chair)**
  - URL: https://georgegriffin.substack.com/
  - Data: Woolpert assessment findings, $28.9M Ephesus estimate
  - Access Date: January 2025
  - Status: ✓ VERIFIED

### Childcare Data
- **NC DHHS Child Care Facility Search**
  - URL: https://ncchildcare.ncdhhs.gov/childcaresearch
  - Data: Licensed childcare centers (name, address, star rating, capacity)
  - Access Date: January 2025
  - Status: ✓ VERIFIED
  - **Search Methodology:**
    - Searched by zip codes: 27510, 27514, 27516, 27517
    - Filtered for "Child Care Center" facility type
    - Deduplicated results (centers may appear in multiple zip searches)
    - Geocoded addresses to lat/lon coordinates
    - Calculated haversine distance to each school
    - Filtered centers within 0.5 miles (805 meters)
  - **Limitations:**
    - Distance is straight-line ("as the crow flies"), not walking distance
    - Results limited to licensed facilities in NC DHHS database
    - Data freshness depends on NC DHHS database update frequency

## Processed Data Files

### Bond Decision Framework
- **2024 Bond Presentation Analysis**
  - File: `data/processed/bond_presentation_2024.md`
  - Data: District decision-making framework, evaluation criteria
  - Source: CHCCS 2024 Bond Project Update Presentation
  - Status: ✓ PROCESSED

### Safe Routes to School Analysis
- **Safe Routes to School Action Plan**
  - File: `data/processed/safe_routes_analysis.md`
  - Source: Town of Chapel Hill, adopted 6/11/2025
  - Data: Student walking distances, active transportation rates, planned infrastructure
  - Key findings: 99 students within 0.5 miles, 20% walk/bike rate
  - Status: ✓ PROCESSED

### Childcare Center Analysis
- **Childcare Centers by School**
  - File: `data/processed/childcare_by_school.csv`
  - Source: NC DHHS Child Care Facility Search
  - Data: Count and total capacity of childcare centers within 0.5 miles of each school
  - Status: ✓ PROCESSED

- **Childcare Centers Detail**
  - File: `data/processed/childcare_centers_detail.csv`
  - Source: NC DHHS Child Care Facility Search
  - Data: Individual center details (name, address, capacity, rating, nearest school, distance)
  - Status: ✓ PROCESSED

### Transportation Data
- **Charlotte Urban Institute**
  - URL: https://ui.charlotte.edu/
  - Data: NC school transportation costs ($575/student, $33K/route)
  - Access Date: January 2025
  - Status: ✓ VERIFIED (NC state data, not CHCCS-specific)

## Key Statistics (with sources)

| Statistic | Value | Source | Status |
|-----------|-------|--------|--------|
| Students within 0.5 miles of Ephesus | 99 | Town of Chapel Hill GIS | ✓ Verified |
| Students walking/biking to Ephesus | 78 (20%) | Safe Routes Tally Nov 2024 | ✓ Verified |
| Ephesus Free/Reduced Lunch % | 30-36% | NCES | ✓ Verified |
| Ephesus Minority Enrollment % | 50% | NCES | ✓ Verified |
| Ephesus Academic Growth Score | 85.8 | NC Report Cards | ✓ Verified |
| Ephesus Academic Growth Rank | 4th of 11 | NC Report Cards | ✓ Verified |
| EC Pre-K Staff at Ephesus | 2 of 3 district-wide | CHCCS | * Unverified |
| Housing units near Ephesus (total) | 563 | Town of Chapel Hill | ✓ Verified |
| Housing units near Ephesus (affordable) | 149 | CH Affordable Housing | ✓ Verified |
| Housing units near Ephesus (market-rate) | 414 | Town of Chapel Hill | ✓ Verified |
| 2024 Bond Total | $300M | CHCCS Bond Documents | ✓ Verified |
| CHCCS Bond Allocation | $174.7M | Chapelboro | ✓ Verified |
| Closure savings (annual) | ~$1.7M | CHCCS Presentation | ✓ Verified |
| Added bus costs (99 students) | ~$57K-$75K | NC estimates | ✓ Verified (NC) |
| Ephesus renovation estimate | $28.9M | Woolpert/Griffin | ✓ Verified |
| Carrboro Elementary Year Built | 1959 | CHCCS Facilities | ✓ Verified |
| Estes Hills Year Built | 1958 | CHCCS Facilities | ✓ Verified |
| FPG Year Built | 1962 | CHCCS Facilities | ✓ Verified |

## Verification Status

- [x] Academic growth data verified (Ephesus = 85.8, #4 of 11, "Exceeded")
- [x] Enrollment numbers verified (389-410 students)
- [x] Cost estimates verified ($1.7M savings, $28.9M renovation)
- [x] Housing development data verified (563 total: 149 affordable + 414 market-rate)
- [x] Walkability data verified (99 students within 0.5 miles - Town of Chapel Hill GIS, Feb 2025)

## Academic Growth Rankings (Verified)

| Rank | School | Growth Score | Status |
|------|--------|--------------|--------|
| 1 | Glenwood | 88.9 | Exceeded |
| 2 | Scroggs | 88.3 | Exceeded |
| 3 | Rashkis | 87.3 | Exceeded |
| 4 | **Ephesus** | **85.8** | **Exceeded** |
| 5 | Morris Grove | 84.4 | Met |
| 6 | Seawell | 82.6 | Met |
| 7 | FPG | 80.9 | Met |
| 8 | Northside | 79.9 | Met |
| 9 | Estes Hills | 74.3 | Met |
| 10 | Carrboro | 64.7 | Did Not Meet |
| 11 | McDougle | 63.2 | Did Not Meet |

## Housing Development by School Zone (Verified)

| School Zone | Total Units | Affordable Units | Rank |
|-------------|-------------|------------------|------|
| Morris Grove | 1,075-1,270 | TBD | 1st |
| FPG/Glen Lennox | 833+ | 0 | 2nd |
| Scroggs (South Creek) | ~815 | ~122 | 3rd |
| **Ephesus** | **563** | **149** | **4th** |
| Estes Hills (Aura) | ~419 | 37 | 5th |
| Northside | 244 | 244 (100%) | 6th |

## Notes
All claims in the final report must be verified against primary sources.
Include footnotes with direct URLs for key statistics.

**Legend:**
- ✓ = Verified with official source
- * = Parent-supplied, needs independent verification
