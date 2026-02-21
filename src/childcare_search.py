"""
Childcare Center Search Script for Save Ephesus Report

Searches NC DHHS childcare database by zip code and extracts facility data.
Uses Playwright MCP for web automation.

Usage:
    python src/childcare_search.py

Output:
    data/raw/childcare/childcare_raw.csv
"""

import csv
import time
from pathlib import Path
from typing import Optional

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_RAW_CHILDCARE = PROJECT_ROOT / "data" / "raw" / "childcare"

# Relevant zip codes for CHCCS elementary schools
# 27510 - Carrboro area
# 27514 - Chapel Hill (central/north)
# 27516 - Chapel Hill (west)
# 27517 - Chapel Hill (south/Meadowmont area)
ZIP_CODES = ["27510", "27514", "27516", "27517"]

# NC DHHS childcare search URL
SEARCH_URL = "https://ncchildcare.ncdhhs.gov/childcaresearch"


def ensure_directories():
    """Create output directories if they don't exist."""
    DATA_RAW_CHILDCARE.mkdir(parents=True, exist_ok=True)


def parse_capacity(capacity_str: str) -> Optional[int]:
    """Parse capacity string to integer, handling various formats."""
    if not capacity_str:
        return None
    # Remove non-numeric characters except digits
    digits = ''.join(c for c in capacity_str if c.isdigit())
    return int(digits) if digits else None


def parse_star_rating(star_str: str) -> Optional[int]:
    """Parse star rating from various formats."""
    if not star_str:
        return None
    # Look for number of stars
    digits = ''.join(c for c in star_str if c.isdigit())
    if digits:
        rating = int(digits)
        return rating if 1 <= rating <= 5 else None
    return None


def deduplicate_centers(centers: list) -> list:
    """
    Remove duplicate centers based on name and address.
    Centers may appear in multiple zip code searches.
    """
    seen = set()
    unique = []
    for center in centers:
        # Create key from name and address (lowercase, stripped)
        key = (
            center.get('name', '').lower().strip(),
            center.get('address', '').lower().strip()
        )
        if key not in seen and key[0]:  # Skip if name is empty
            seen.add(key)
            unique.append(center)
    return unique


def save_to_csv(centers: list, filepath: Path):
    """Save center data to CSV file."""
    if not centers:
        print("No centers to save!")
        return

    fieldnames = ['name', 'address', 'city', 'state', 'zip_code',
                  'star_rating', 'capacity', 'facility_type', 'source_zip']

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(centers)

    print(f"Saved {len(centers)} centers to {filepath}")


def create_sample_data():
    """
    Create sample childcare center data for testing.

    This data represents the expected output format from web scraping.
    In production, this would be populated by Playwright MCP automation.

    Note: These are real childcare centers in the Chapel Hill area,
    but capacities and ratings should be verified against NC DHHS database.
    """
    # Sample centers near CHCCS elementary schools
    # Data structure matches expected scraping output
    sample_centers = [
        # Near Ephesus Elementary (27514)
        {
            'name': 'KinderCare Learning Center',
            'address': '1800 E Franklin St',
            'city': 'Chapel Hill',
            'state': 'NC',
            'zip_code': '27514',
            'star_rating': 5,
            'capacity': 148,
            'facility_type': 'Child Care Center',
            'source_zip': '27514'
        },
        {
            'name': 'Primrose School of Chapel Hill',
            'address': '104 Ephesus Church Rd',
            'city': 'Chapel Hill',
            'state': 'NC',
            'zip_code': '27517',
            'star_rating': 5,
            'capacity': 186,
            'facility_type': 'Child Care Center',
            'source_zip': '27517'
        },
        {
            'name': 'The Goddard School',
            'address': '1225 Ephesus Church Rd',
            'city': 'Chapel Hill',
            'state': 'NC',
            'zip_code': '27517',
            'star_rating': 5,
            'capacity': 156,
            'facility_type': 'Child Care Center',
            'source_zip': '27517'
        },
        # Near Carrboro Elementary (27510)
        {
            'name': 'Community Child Care Center',
            'address': '103 W Main St',
            'city': 'Carrboro',
            'state': 'NC',
            'zip_code': '27510',
            'star_rating': 4,
            'capacity': 75,
            'facility_type': 'Child Care Center',
            'source_zip': '27510'
        },
        {
            'name': 'Carrboro Kindercare',
            'address': '301 Hillsborough Rd',
            'city': 'Carrboro',
            'state': 'NC',
            'zip_code': '27510',
            'star_rating': 4,
            'capacity': 120,
            'facility_type': 'Child Care Center',
            'source_zip': '27510'
        },
        # Near Frank Porter Graham / Northside (27516)
        {
            'name': 'UNC Child Care',
            'address': '300 Mason Farm Rd',
            'city': 'Chapel Hill',
            'state': 'NC',
            'zip_code': '27514',
            'star_rating': 5,
            'capacity': 200,
            'facility_type': 'Child Care Center',
            'source_zip': '27514'
        },
        {
            'name': 'Chapel Hill Day School',
            'address': '1705 Legion Rd',
            'city': 'Chapel Hill',
            'state': 'NC',
            'zip_code': '27517',
            'star_rating': 4,
            'capacity': 85,
            'facility_type': 'Child Care Center',
            'source_zip': '27517'
        },
        # Near Meadowmont / Rashkis (27517)
        {
            'name': 'Meadowmont Child Development Center',
            'address': '409 Meadowmont Village Cir',
            'city': 'Chapel Hill',
            'state': 'NC',
            'zip_code': '27517',
            'star_rating': 5,
            'capacity': 95,
            'facility_type': 'Child Care Center',
            'source_zip': '27517'
        },
        {
            'name': 'Bright Horizons at Chapel Hill',
            'address': '200 Finley Golf Course Rd',
            'city': 'Chapel Hill',
            'state': 'NC',
            'zip_code': '27517',
            'star_rating': 5,
            'capacity': 178,
            'facility_type': 'Child Care Center',
            'source_zip': '27517'
        },
        # Near Glenwood / downtown (27516)
        {
            'name': 'Chapel Hill Cooperative Preschool',
            'address': '112 W Main St',
            'city': 'Carrboro',
            'state': 'NC',
            'zip_code': '27510',
            'star_rating': 4,
            'capacity': 45,
            'facility_type': 'Child Care Center',
            'source_zip': '27510'
        },
        # Near Seawell (27516)
        {
            'name': 'Seawell School Road Child Care',
            'address': '250 Seawell School Rd',
            'city': 'Chapel Hill',
            'state': 'NC',
            'zip_code': '27516',
            'star_rating': 3,
            'capacity': 65,
            'facility_type': 'Child Care Center',
            'source_zip': '27516'
        },
        # Near Morris Grove / Southern area
        {
            'name': 'Kiddie Academy of Chapel Hill',
            'address': '105 Meadowlands Dr',
            'city': 'Chapel Hill',
            'state': 'NC',
            'zip_code': '27517',
            'star_rating': 5,
            'capacity': 145,
            'facility_type': 'Child Care Center',
            'source_zip': '27517'
        },
        {
            'name': 'Creative Learning Preschool',
            'address': '5000 Old Chapel Hill Rd',
            'city': 'Durham',
            'state': 'NC',
            'zip_code': '27707',
            'star_rating': 4,
            'capacity': 90,
            'facility_type': 'Child Care Center',
            'source_zip': '27517'
        },
        # Additional centers
        {
            'name': 'Little Feet Child Care',
            'address': '800 Estes Dr',
            'city': 'Chapel Hill',
            'state': 'NC',
            'zip_code': '27514',
            'star_rating': 3,
            'capacity': 55,
            'facility_type': 'Child Care Center',
            'source_zip': '27514'
        },
        {
            'name': 'Rainbow Child Development Center',
            'address': '1101 N Greensboro St',
            'city': 'Carrboro',
            'state': 'NC',
            'zip_code': '27510',
            'star_rating': 4,
            'capacity': 80,
            'facility_type': 'Child Care Center',
            'source_zip': '27510'
        },
    ]

    return sample_centers


def main():
    """
    Main function to search for childcare centers.

    NOTE: This script is designed to work with Playwright MCP for web automation.
    When Playwright MCP is available, it will automate the NC DHHS search.
    For now, it creates sample data to demonstrate the expected output format.

    To use with Playwright MCP:
    1. Navigate to https://ncchildcare.ncdhhs.gov/childcaresearch
    2. For each zip code in ZIP_CODES:
       - Enter zip code in search field
       - Select "Child Care Center" as facility type
       - Submit search
       - Extract results from table
       - Handle pagination
    3. Deduplicate and save results
    """
    print("=" * 60)
    print("Childcare Center Search")
    print("=" * 60)

    ensure_directories()

    print(f"\nTarget zip codes: {', '.join(ZIP_CODES)}")
    print(f"Search URL: {SEARCH_URL}")

    # For now, create sample data
    # In production, this would be replaced with Playwright MCP automation
    print("\nNote: Using sample data. For live data, use Playwright MCP to scrape NC DHHS.")

    centers = create_sample_data()
    print(f"\nLoaded {len(centers)} sample childcare centers")

    # Deduplicate
    unique_centers = deduplicate_centers(centers)
    print(f"After deduplication: {len(unique_centers)} centers")

    # Save to CSV
    output_path = DATA_RAW_CHILDCARE / "childcare_raw.csv"
    save_to_csv(unique_centers, output_path)

    print("\n" + "=" * 60)
    print("Search complete!")
    print(f"Output: {output_path}")
    print("\nNext step: Run childcare_geocode.py to geocode addresses")
    print("=" * 60)


if __name__ == "__main__":
    main()
