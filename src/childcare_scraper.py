"""
Childcare Facility Web Scraper for NC DHHS

Uses Playwright to scrape childcare facility data from NC DHHS database.
Searches by zip code and facility type (Child Care Centers and Family Child Care Homes).

Usage:
    python src/childcare_scraper.py

Output:
    data/raw/childcare/childcare_centers_raw.csv
    data/raw/childcare/childcare_family_homes_raw.csv
    data/raw/childcare/childcare_all_raw.csv
"""

import csv
import re
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_RAW_CHILDCARE = PROJECT_ROOT / "data" / "raw" / "childcare"

# Relevant zip codes for CHCCS elementary schools
ZIP_CODES = ["27510", "27514", "27516", "27517"]

# Facility types to search
FACILITY_TYPES = ["Child Care Center", "Family Child Care Home"]

# NC DHHS childcare search URL
SEARCH_URL = "https://ncchildcare.ncdhhs.gov/childcaresearch"

# Element IDs from the NC DHHS form
ZIP_CODE_INPUT_ID = "#dnn_ctr1464_View_txtZipCode"
FACILITY_TYPE_SELECT_ID = "#dnn_ctr1464_View_ddlFacilityType"
SEARCH_BUTTON_ID = "#dnn_ctr1464_View_btnSearch"


def ensure_directories():
    """Create output directories if they don't exist."""
    DATA_RAW_CHILDCARE.mkdir(parents=True, exist_ok=True)


def parse_address_cell(address_text):
    """
    Parse the address cell which contains:
    - Street address
    - City, State Zip
    - Phone number

    Returns: (street, city, state, zip_code, phone)
    """
    lines = [l.strip() for l in address_text.strip().split('\n') if l.strip()]

    street = ''
    city = ''
    state = 'NC'
    zip_code = ''
    phone = ''

    for line in lines:
        # Check for phone number
        phone_match = re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', line)
        if phone_match:
            phone = phone_match.group()
            continue

        # Check for city, state, zip pattern
        city_match = re.search(r'^([A-Za-z\s]+),\s*NC\s+(\d{5})', line)
        if city_match:
            city = city_match.group(1).strip()
            zip_code = city_match.group(2)
            continue

        # Otherwise it's probably the street address
        if not street and line:
            street = line

    return street, city, state, zip_code, phone


def scrape_search_results(page, source_zip):
    """
    Extract childcare center data from the current search results page.

    Table structure:
    - Column 0: License Number
    - Column 1: Facility Name (link)
    - Column 2: Address (multi-line)
    - Column 3: Facility Type

    Returns list of center dictionaries.
    """
    centers = []

    # Wait for results to load
    time.sleep(2)

    # Get result rows (skip header row)
    rows = page.query_selector_all('table tbody tr')

    if not rows:
        # Try without tbody
        rows = page.query_selector_all('table tr')
        # Skip header row if present
        if rows:
            first_row_text = rows[0].inner_text().lower()
            if 'license' in first_row_text or 'facility' in first_row_text:
                rows = rows[1:]

    print(f"    Found {len(rows)} result rows")

    for row in rows:
        try:
            cells = row.query_selector_all('td')
            if len(cells) < 4:
                continue

            # Extract data from cells
            license_num = cells[0].inner_text().strip()

            # Facility name - might be in a link
            name_link = cells[1].query_selector('a')
            if name_link:
                name = name_link.inner_text().strip()
            else:
                name = cells[1].inner_text().strip()

            # Address cell (multi-line)
            address_text = cells[2].inner_text()
            street, city, state, zip_code, phone = parse_address_cell(address_text)

            # Facility type
            facility_type = cells[3].inner_text().strip()

            # Skip header rows
            if 'license' in license_num.lower() or 'facility' in name.lower():
                continue

            if name:
                # Build full address
                full_address = street
                if city:
                    full_address = f"{street}, {city}, NC {zip_code}"

                centers.append({
                    'name': name,
                    'license_number': license_num,
                    'address': full_address,
                    'city': city,
                    'state': state,
                    'zip_code': zip_code or source_zip,
                    'phone': phone,
                    'star_rating': None,  # Not shown in list view
                    'capacity': None,      # Not shown in list view
                    'facility_type': facility_type or 'Child Care Center',
                    'source_zip': source_zip
                })

        except Exception as e:
            print(f"    Error parsing row: {e}")
            continue

    return centers


def search_by_zip(page, zip_code, facility_type="Child Care Center"):
    """
    Perform a search for childcare facilities by zip code and facility type.

    Args:
        page: Playwright page object
        zip_code: Zip code to search
        facility_type: Type of facility ("Child Care Center" or "Family Child Care Home")

    Returns list of facility dictionaries.
    """
    all_facilities = []

    print(f"\n  Searching zip code: {zip_code} for '{facility_type}'")

    try:
        # Navigate to search page
        page.goto(SEARCH_URL, wait_until='networkidle', timeout=30000)
        time.sleep(2)

        # Wait for the form to load
        page.wait_for_selector(ZIP_CODE_INPUT_ID, timeout=10000)

        # Fill in the zip code
        zip_input = page.query_selector(ZIP_CODE_INPUT_ID)
        if zip_input:
            zip_input.click()
            time.sleep(0.2)
            zip_input.fill(zip_code)
            print(f"    Filled zip code: {zip_code}")
        else:
            print("    ERROR: Could not find zip code input")
            return all_facilities

        # Select facility type from dropdown
        try:
            page.select_option(FACILITY_TYPE_SELECT_ID, value=facility_type)
            print(f"    Selected '{facility_type}'")
        except Exception as e:
            print(f"    Note: Could not select facility type: {e}")
            try:
                page.select_option(FACILITY_TYPE_SELECT_ID, label=facility_type)
            except:
                pass

        # Click the Search button
        search_btn = page.query_selector(SEARCH_BUTTON_ID)
        if search_btn:
            search_btn.click()
            print("    Clicked Search button")
        else:
            print("    ERROR: Could not find search button")
            return all_facilities

        # Wait for results to load
        time.sleep(3)
        page.wait_for_load_state('networkidle', timeout=20000)

        # Take screenshot of results (include facility type in filename)
        type_suffix = "centers" if "Center" in facility_type else "family"
        page.screenshot(path=str(DATA_RAW_CHILDCARE / f"results_{zip_code}_{type_suffix}.png"), full_page=True)

        # Check for record count
        record_count_el = page.query_selector('.alert-success, .badge, [class*="record"]')
        if record_count_el:
            count_text = record_count_el.inner_text()
            print(f"    {count_text}")

        # Extract results
        facilities = scrape_search_results(page, zip_code)
        # Ensure facility_type is set correctly for each record
        for f in facilities:
            f['facility_type'] = facility_type
        all_facilities.extend(facilities)
        print(f"    Found {len(facilities)} facilities")

        # Check for pagination
        page_num = 1
        while True:
            next_link = page.query_selector('a:has-text("Next"), a.next, .pagination a:has-text(">")')
            if next_link and next_link.is_visible():
                try:
                    next_link.click()
                    page.wait_for_load_state('networkidle', timeout=15000)
                    time.sleep(2)
                    page_num += 1
                    print(f"    Processing page {page_num}...")

                    additional = scrape_search_results(page, zip_code)
                    for f in additional:
                        f['facility_type'] = facility_type
                    all_facilities.extend(additional)
                    print(f"    Found {len(additional)} more facilities on page {page_num}")
                except Exception as e:
                    print(f"    Pagination error: {e}")
                    break
            else:
                break

    except Exception as e:
        print(f"    Error: {e}")
        try:
            page.screenshot(path=str(DATA_RAW_CHILDCARE / f"error_{zip_code}_{type_suffix}.png"))
        except:
            pass

    return all_facilities


def deduplicate_centers(centers):
    """Remove duplicate centers based on license number or name+address."""
    seen_licenses = set()
    seen_names = set()
    unique = []

    for center in centers:
        license_num = center.get('license_number', '').strip()
        name_addr_key = (
            center.get('name', '').lower().strip(),
            center.get('address', '').lower().strip()[:50]
        )

        # Skip if we've seen this license number
        if license_num and license_num in seen_licenses:
            continue

        # Skip if we've seen this name+address combo
        if name_addr_key[0] and name_addr_key in seen_names:
            continue

        if license_num:
            seen_licenses.add(license_num)
        if name_addr_key[0]:
            seen_names.add(name_addr_key)

        unique.append(center)

    return unique


def save_to_csv(centers, filepath):
    """Save centers to CSV file."""
    if not centers:
        print("No centers to save!")
        return

    fieldnames = ['name', 'license_number', 'address', 'city', 'state', 'zip_code',
                  'phone', 'star_rating', 'capacity', 'facility_type', 'source_zip']

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(centers)

    print(f"\nSaved {len(centers)} centers to {filepath}")


def main():
    """Main function to scrape childcare facilities (centers and family homes)."""
    print("=" * 60)
    print("NC DHHS Childcare Facility Scraper")
    print("=" * 60)

    ensure_directories()

    print(f"\nTarget zip codes: {', '.join(ZIP_CODES)}")
    print(f"Facility types: {', '.join(FACILITY_TYPES)}")
    print(f"Search URL: {SEARCH_URL}")

    # Store facilities by type
    facilities_by_type = {ftype: [] for ftype in FACILITY_TYPES}

    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1280, 'height': 900},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = context.new_page()

        # Search each facility type and zip code
        for facility_type in FACILITY_TYPES:
            print(f"\n{'='*60}")
            print(f"Searching for: {facility_type}")
            print("=" * 60)

            for zip_code in ZIP_CODES:
                facilities = search_by_zip(page, zip_code, facility_type)
                facilities_by_type[facility_type].extend(facilities)
                time.sleep(1)

        browser.close()

    # Process and save each type separately
    all_facilities = []

    for facility_type in FACILITY_TYPES:
        raw_count = len(facilities_by_type[facility_type])
        print(f"\n{facility_type}: {raw_count} found")

        unique = deduplicate_centers(facilities_by_type[facility_type])
        print(f"After deduplication: {len(unique)} unique")

        facilities_by_type[facility_type] = unique
        all_facilities.extend(unique)

        # Save type-specific file
        if "Center" in facility_type:
            output_path = DATA_RAW_CHILDCARE / "childcare_centers_raw.csv"
        else:
            output_path = DATA_RAW_CHILDCARE / "childcare_family_homes_raw.csv"

        save_to_csv(unique, output_path)

    # Deduplicate combined list (shouldn't have overlaps but just in case)
    unique_all = deduplicate_centers(all_facilities)

    # Save combined file
    all_output_path = DATA_RAW_CHILDCARE / "childcare_all_raw.csv"
    save_to_csv(unique_all, all_output_path)

    # Print summary
    print("\n" + "=" * 60)
    print("Scraping complete!")
    print("=" * 60)
    print("\nSummary:")
    for facility_type in FACILITY_TYPES:
        count = len(facilities_by_type[facility_type])
        print(f"  - {facility_type}: {count}")
    print(f"  - Total (combined): {len(unique_all)}")

    print("\nOutput files:")
    print(f"  - {DATA_RAW_CHILDCARE / 'childcare_centers_raw.csv'}")
    print(f"  - {DATA_RAW_CHILDCARE / 'childcare_family_homes_raw.csv'}")
    print(f"  - {DATA_RAW_CHILDCARE / 'childcare_all_raw.csv'}")
    print("\nCheck screenshots in data/raw/childcare/ for results.")
    print("Next step: Run childcare_geocode.py to process the data")
    print("=" * 60)


if __name__ == "__main__":
    main()
