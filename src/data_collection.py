"""
Data Collection Module for Save Ephesus Elementary Report

This module gathers data from official sources including:
- NC School Report Cards (academic performance)
- CHCCS School Profiles
- NCES enrollment data
- Town of Chapel Hill housing data
"""

import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"

# CHCCS Elementary Schools
CHCCS_ELEMENTARY_SCHOOLS = [
    {"name": "Ephesus Elementary", "nces_id": "370297001545"},
    {"name": "Carrboro Elementary", "nces_id": "370297000214"},
    {"name": "Estes Hills Elementary", "nces_id": "370297000215"},
    {"name": "Frank Porter Graham Bilingue", "nces_id": "370297000216"},
    {"name": "Glenwood Elementary", "nces_id": "370297000217"},
    {"name": "McDougle Elementary", "nces_id": "370297000218"},
    {"name": "Morris Grove Elementary", "nces_id": "370297001476"},
    {"name": "Northside Elementary", "nces_id": "370297000220"},
    {"name": "Rashkis Elementary", "nces_id": "370297001340"},
    {"name": "Scroggs Elementary", "nces_id": "370297001414"},
    {"name": "Seawell Elementary", "nces_id": "370297000221"},
]

# Data source URLs
SOURCES = {
    "nc_report_cards": "https://www.dpi.nc.gov/data-reports/school-report-cards",
    "chccs_profiles": "https://www.chccs.org",
    "nces_search": "https://nces.ed.gov/ccd/schoolsearch/",
    "chccs_bond": "https://www.chccs.org/community/schoolbond/overview",
    "chapel_hill_housing": "https://www.townofchapelhill.org",
}


def ensure_directories():
    """Create necessary data directories if they don't exist."""
    DATA_RAW.mkdir(parents=True, exist_ok=True)
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    (DATA_RAW / "nc_report_cards").mkdir(exist_ok=True)
    (DATA_RAW / "chccs_profiles").mkdir(exist_ok=True)
    (DATA_RAW / "housing_data").mkdir(exist_ok=True)


def create_manual_data_template():
    """
    Create template CSV files for manual data entry.
    Some data must be manually collected from official sources.
    """

    # Enrollment and demographics template
    enrollment_template = pd.DataFrame({
        "school": [s["name"] for s in CHCCS_ELEMENTARY_SCHOOLS],
        "enrollment_2024": [None] * len(CHCCS_ELEMENTARY_SCHOOLS),
        "capacity": [None] * len(CHCCS_ELEMENTARY_SCHOOLS),
        "free_reduced_lunch_pct": [None] * len(CHCCS_ELEMENTARY_SCHOOLS),
        "minority_pct": [None] * len(CHCCS_ELEMENTARY_SCHOOLS),
        "title_i": [None] * len(CHCCS_ELEMENTARY_SCHOOLS),
        "students_within_half_mile": [None] * len(CHCCS_ELEMENTARY_SCHOOLS),
        "walk_bike_pct": [None] * len(CHCCS_ELEMENTARY_SCHOOLS),
    })

    # Pre-fill known Ephesus data
    ephesus_idx = 0  # Ephesus is first in list
    enrollment_template.loc[ephesus_idx, "students_within_half_mile"] = 99
    enrollment_template.loc[ephesus_idx, "free_reduced_lunch_pct"] = 38
    enrollment_template.loc[ephesus_idx, "minority_pct"] = 50
    enrollment_template.loc[ephesus_idx, "title_i"] = True

    enrollment_template.to_csv(DATA_PROCESSED / "enrollment.csv", index=False)
    print(f"Created template: {DATA_PROCESSED / 'enrollment.csv'}")

    # Academic growth template
    academic_template = pd.DataFrame({
        "school": [s["name"] for s in CHCCS_ELEMENTARY_SCHOOLS],
        "growth_score_2024": [None] * len(CHCCS_ELEMENTARY_SCHOOLS),
        "growth_status": [None] * len(CHCCS_ELEMENTARY_SCHOOLS),
        "reading_proficiency": [None] * len(CHCCS_ELEMENTARY_SCHOOLS),
        "math_proficiency": [None] * len(CHCCS_ELEMENTARY_SCHOOLS),
        "school_performance_grade": [None] * len(CHCCS_ELEMENTARY_SCHOOLS),
    })

    # Note: Ephesus has highest growth - to be filled with actual data
    academic_template.loc[ephesus_idx, "growth_status"] = "Highest in District"

    academic_template.to_csv(DATA_PROCESSED / "academic_growth.csv", index=False)
    print(f"Created template: {DATA_PROCESSED / 'academic_growth.csv'}")

    # Cost analysis template
    costs_template = pd.DataFrame({
        "school": [s["name"] for s in CHCCS_ELEMENTARY_SCHOOLS],
        "year_built": [None] * len(CHCCS_ELEMENTARY_SCHOOLS),
        "renovation_cost_estimate": [None] * len(CHCCS_ELEMENTARY_SCHOOLS),
        "annual_operating_cost": [None] * len(CHCCS_ELEMENTARY_SCHOOLS),
        "bond_funding_2024": [None] * len(CHCCS_ELEMENTARY_SCHOOLS),
    })

    # Known bond data
    bond_schools = {
        "Carrboro Elementary": {"year_built": 1959, "bond_funding_2024": True},
        "Estes Hills Elementary": {"year_built": 1958, "bond_funding_2024": True},
        "Frank Porter Graham Bilingue": {"year_built": 1962, "bond_funding_2024": True},
    }

    for idx, row in costs_template.iterrows():
        if row["school"] in bond_schools:
            costs_template.loc[idx, "year_built"] = bond_schools[row["school"]]["year_built"]
            costs_template.loc[idx, "bond_funding_2024"] = bond_schools[row["school"]]["bond_funding_2024"]

    costs_template.to_csv(DATA_PROCESSED / "costs.csv", index=False)
    print(f"Created template: {DATA_PROCESSED / 'costs.csv'}")

    # Demographics template
    demographics_template = pd.DataFrame({
        "school": [s["name"] for s in CHCCS_ELEMENTARY_SCHOOLS],
        "white_pct": [None] * len(CHCCS_ELEMENTARY_SCHOOLS),
        "black_pct": [None] * len(CHCCS_ELEMENTARY_SCHOOLS),
        "hispanic_pct": [None] * len(CHCCS_ELEMENTARY_SCHOOLS),
        "asian_pct": [None] * len(CHCCS_ELEMENTARY_SCHOOLS),
        "multiracial_pct": [None] * len(CHCCS_ELEMENTARY_SCHOOLS),
        "ec_prek_staff": [None] * len(CHCCS_ELEMENTARY_SCHOOLS),
    })

    # Known Ephesus data
    demographics_template.loc[ephesus_idx, "ec_prek_staff"] = 2  # 2 of 3 EC Pre-K staff

    demographics_template.to_csv(DATA_PROCESSED / "demographics.csv", index=False)
    print(f"Created template: {DATA_PROCESSED / 'demographics.csv'}")


def create_housing_data():
    """Create housing development data for Ephesus area."""
    housing_data = pd.DataFrame([
        {
            "project_name": "Greenfield Place (Phase 1)",
            "units": 80,
            "type": "Working Families",
            "status": "Completed",
            "near_ephesus": True,
            "lat": 35.9382,
            "lon": -79.0208,
        },
        {
            "project_name": "Greenfield Commons (Phase 2)",
            "units": 69,
            "type": "Seniors",
            "status": "Completed",
            "near_ephesus": True,
            "lat": 35.9378,
            "lon": -79.0215,
        },
        {
            "project_name": "Park Apartments",
            "address": "1250 Ephesus Church Road",
            "units": 414,
            "type": "Mixed Income",
            "status": "Under Construction",
            "near_ephesus": True,
            "lat": 35.9405,
            "lon": -79.0180,
        },
    ])

    housing_data.to_csv(DATA_RAW / "housing_data" / "affordable_housing.csv", index=False)
    print(f"Created: {DATA_RAW / 'housing_data' / 'affordable_housing.csv'}")

    return housing_data


def create_school_locations():
    """Create school location data for mapping."""
    # Approximate coordinates for CHCCS elementary schools
    locations = pd.DataFrame([
        {"school": "Ephesus Elementary", "lat": 35.9372, "lon": -79.0178, "address": "1495 Ephesus Church Rd"},
        {"school": "Carrboro Elementary", "lat": 35.9103, "lon": -79.0753, "address": "400 Shelton St"},
        {"school": "Estes Hills Elementary", "lat": 35.9442, "lon": -79.0467, "address": "500 Estes Dr Ext"},
        {"school": "Frank Porter Graham Bilingue", "lat": 35.9285, "lon": -79.0392, "address": "101 Smith Level Rd"},
        {"school": "Glenwood Elementary", "lat": 35.9128, "lon": -79.0589, "address": "211 N Greensboro St"},
        {"school": "McDougle Elementary", "lat": 35.8983, "lon": -79.0453, "address": "900 Old Fayetteville Rd"},
        {"school": "Morris Grove Elementary", "lat": 35.8775, "lon": -79.0308, "address": "215 Eubanks Rd"},
        {"school": "Northside Elementary", "lat": 35.9225, "lon": -79.0567, "address": "330 Caldwell St"},
        {"school": "Rashkis Elementary", "lat": 35.8817, "lon": -79.0692, "address": "601 Meadowmont Ln"},
        {"school": "Scroggs Elementary", "lat": 35.8650, "lon": -79.0433, "address": "501 Kildaire Farm Rd"},
        {"school": "Seawell Elementary", "lat": 35.9033, "lon": -79.0817, "address": "200 Seawell School Rd"},
    ])

    locations.to_csv(DATA_PROCESSED / "school_locations.csv", index=False)
    print(f"Created: {DATA_PROCESSED / 'school_locations.csv'}")

    return locations


def create_sources_documentation():
    """Create sources.md with citation tracking."""
    sources_content = """# Data Sources for Save Ephesus Report

## Official Sources

### Academic Performance
- **NC School Report Cards**
  - URL: https://www.dpi.nc.gov/data-reports/school-report-cards
  - Data: Academic growth, proficiency rates, school grades
  - Access Date: [TO BE FILLED]

### Enrollment Data
- **NCES Common Core of Data**
  - URL: https://nces.ed.gov/ccd/schoolsearch/
  - Data: Enrollment, demographics, Title I status
  - Access Date: [TO BE FILLED]

### District Information
- **CHCCS Official Website**
  - URL: https://www.chccs.org
  - Data: School profiles, capacity, programs
  - Access Date: [TO BE FILLED]

### Bond Information
- **CHCCS School Bond**
  - URL: https://www.chccs.org/community/schoolbond/overview
  - Data: $300M bond allocation, renovation costs
  - Access Date: [TO BE FILLED]

### Housing Development
- **Town of Chapel Hill**
  - URL: https://www.townofchapelhill.org
  - Data: Affordable housing projects, development plans
  - Access Date: [TO BE FILLED]

- **Chapel Hill Affordable Housing**
  - URL: https://www.chapelhillaffordablehousing.org
  - Data: Project details, unit counts
  - Access Date: [TO BE FILLED]

## Key Statistics (with sources)

| Statistic | Value | Source |
|-----------|-------|--------|
| Students within 0.5 miles of Ephesus | 99 | CHCCS Transportation Data |
| Ephesus Free/Reduced Lunch % | 38% | NC School Report Cards |
| Ephesus Minority Enrollment % | 50% | NCES |
| EC Pre-K Staff at Ephesus | 2 of 3 district-wide | CHCCS |
| New housing units near Ephesus | 563+ | Town of Chapel Hill |
| 2024 Bond Total | $300M | CHCCS Bond Documents |
| Carrboro Elementary Year Built | 1959 | CHCCS Facilities |
| Estes Hills Year Built | 1958 | CHCCS Facilities |
| FPG Year Built | 1962 | CHCCS Facilities |

## Verification Status

- [ ] Academic growth data verified
- [ ] Enrollment numbers verified
- [ ] Cost estimates verified
- [ ] Housing development data verified
- [ ] Walkability data verified

## Notes
All claims in the final report must be verified against primary sources.
Include footnotes with direct URLs for key statistics.
"""

    sources_path = PROJECT_ROOT / "data" / "sources.md"
    with open(sources_path, "w") as f:
        f.write(sources_content)
    print(f"Created: {sources_path}")


def main():
    """Run all data collection tasks."""
    print("=" * 60)
    print("Save Ephesus Elementary - Data Collection")
    print("=" * 60)

    ensure_directories()

    print("\n1. Creating data templates...")
    create_manual_data_template()

    print("\n2. Creating housing data...")
    create_housing_data()

    print("\n3. Creating school locations...")
    create_school_locations()

    print("\n4. Creating sources documentation...")
    create_sources_documentation()

    print("\n" + "=" * 60)
    print("Data collection complete!")
    print("\nNext steps:")
    print("1. Fill in the template CSVs in data/processed/ with actual data")
    print("2. Download NC School Report Card data to data/raw/nc_report_cards/")
    print("3. Run data_processing.py to clean and prepare data")
    print("=" * 60)


if __name__ == "__main__":
    main()
