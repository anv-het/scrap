import requests
from bs4 import BeautifulSoup
import json
import re # For regular expressions to clean text

# --- Helper Functions for Table Extraction ---

def extract_key_value_table(table_soup):
    """
    Extracts data from tables where the first column is the key and the second is the value.
    Handles links in the value column.
    """
    data = {}
    if not table_soup:
        return data

    tbody = table_soup.find('tbody')
    if not tbody:
        return data

    for row in tbody.find_all('tr'):
        cols = row.find_all(['td', 'th']) # Check both td and th for robustness
        if len(cols) == 2:
            key = cols[0].get_text(strip=True).replace(':', '').replace('*', '').strip()
            # Handle links (DRHP, RHP, Anchor List) that have an 'a' tag with href
            link_tag = cols[1].find('a', href=True)
            if link_tag and 'href' in link_tag.attrs:
                value = link_tag['href']
            else:
                value = cols[1].get_text(strip=True)
            data[key] = value
    return data

# Placeholder functions for other extractions (currently not used in this step)
def extract_gmp_table(table_soup):
    return []

def extract_financial_table(table_soup):
    return []

def extract_peer_comparison_table(table_soup):
    return []

def extract_ipo_objective_table(table_soup):
    return []

def extract_bidding_live_updates_table(table_soup):
    return []

# --- Main Scraper Functions ---

def fetch_and_parse_single_ipo_details(url):
    """
    Fetches the HTML content from the given URL and parses only the IPO Name
    and IPO Details table for this step.

    Args:
        url (str): The URL of the IPO details page.

    Returns:
        dict: A dictionary containing the extracted IPO Name and IPO Details,
              or an error message if fetching or parsing fails.
    """
    ipo_data = {}
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15) # Increased timeout
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        html_content = response.text

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return {"error": f"Failed to fetch page: {e}"}

    soup = BeautifulSoup(html_content, 'html.parser')

    # 1. IPO Name
    ipo_name_tag_container = soup.find('div', class_='col-lg-6')
    if ipo_name_tag_container:
        h1_tag = ipo_name_tag_container.find('h1')
        if h1_tag:
            ipo_name_full = h1_tag.get_text(strip=True)
            # Make replacement more general for "IPO Details 2025" and "SME IPO Details 2025"
            ipo_name = re.sub(r'(?:SME )?IPO Details 2025', '', ipo_name_full).strip()
            ipo_data['IPO Name'] = ipo_name
        else:
            ipo_data['IPO Name'] = "N/A (H1 tag not found in col-lg-6)"
    else:
        ipo_data['IPO Name'] = "N/A (col-lg-6 div for IPO name not found)"

    # 2. IPO Details (Table) - First table in the col-lg-6 block
    # This is the first div with itemprop="http://schema.org/Table" inside the first .col-lg-6
    ipo_details_section = None
    
    # Safely find the 'row g-0' div first
    row_g0_container = soup.find('div', class_='row g-0')
    if row_g0_container:
        first_col_lg_6_group = row_g0_container.find('div', class_='col-lg-6 col-md-6 col-sm-12')
        if first_col_lg_6_group:
            ipo_details_section = first_col_lg_6_group.find('div', itemprop='http://schema.org/Table')
    
    if ipo_details_section:
        h2_title = ipo_details_section.find('h2', itemprop='about')
        # Updated check: look for "IPO Details" or "SME IPO Details" in the H2 title
        if h2_title and re.search(r'(?:SME )?IPO Details', h2_title.get_text()):
            table = ipo_details_section.find('table', class_='table')
            ipo_data["IPO Details"] = extract_key_value_table(table)
        else:
            ipo_data["IPO Details"] = {} # Default to empty if correct H2 title not found
    else:
        ipo_data["IPO Details"] = {} # Default to empty if section not found

    # Set other sections to empty/N/A for now as per step-by-step request
    ipo_data['IPO Image URL'] = "N/A (Skipped for this step)"
    ipo_data['About Company Description'] = "N/A (Skipped for this step)"
    ipo_data["IPO Important Dates"] = {}
    ipo_data["IPO Lots"] = {}
    ipo_data["IPO GMP"] = []
    ipo_data['IPO Strengths'] = []
    ipo_data["Company General Information"] = {}
    ipo_data["IPO Objective"] = []
    ipo_data["Live Subscription Summary"] = {}
    ipo_data["IPO Bidding Live Updates"] = []
    ipo_data["Company Financial Information (Restated Consolidated)"] = []
    ipo_data["IPO Peer Comparison"] = []
    ipo_data["Contact & Management Details"] = {}
    ipo_data['Last Updated'] = "N/A (Skipped for this step)"

    return ipo_data


def scrape_all_ipos():
    """
    Fetches the list of all IPOs from the API, then scrapes only the
    "IPO Details" information for each IPO.
    """
    ipo_list_api_url = "https://webnodejs.investorgain.com/cloud/ipo/list-read"
    all_ipos_data = []

    print(f"Fetching IPO list from API: {ipo_list_api_url}")
    try:
        api_response = requests.get(ipo_list_api_url, timeout=10)
        api_response.raise_for_status()
        ipo_list_json = api_response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching IPO list API: {e}")
        return {"error": f"Failed to fetch IPO list: {e}"}

    if ipo_list_json and "ipoList" in ipo_list_json:
        total_ipos = len(ipo_list_json["ipoList"])
        print(f"Found {total_ipos} IPOs to process.")
        
        for i, ipo_entry in enumerate(ipo_list_json["ipoList"]):
            ipo_id = ipo_entry.get("id")
            urlrewrite_folder_name = ipo_entry.get("urlrewrite_folder_name")
            company_short_name = ipo_entry.get("company_short_name", "Unknown Company")

            if ipo_id and urlrewrite_folder_name:
                # Construct the detailed IPO page URL
                ipo_detail_url = f"https://www.investorgain.com/ipo/{urlrewrite_folder_name}/{ipo_id}/"
                
                print(f"\n({i+1}/{total_ipos}) Scraping 'IPO Details' for: {company_short_name} (ID: {ipo_id}) from {ipo_detail_url}")
                
                single_ipo_data = fetch_and_parse_single_ipo_details(ipo_detail_url)
                if "error" not in single_ipo_data:
                    # Add some basic info from the list API to the detailed data
                    single_ipo_data['IPO_List_API_ID'] = ipo_id
                    single_ipo_data['IPO_List_API_Short_Name'] = company_short_name
                    all_ipos_data.append(single_ipo_data)
                else:
                    print(f"Skipping {company_short_name} due to error: {single_ipo_data['error']}")
            else:
                print(f"Skipping IPO entry due to missing ID or URL folder name: {ipo_entry}")

    return {"all_ipos_data": all_ipos_data}

# --- Main execution block ---
if __name__ == "__main__":
    full_scrape_result = scrape_all_ipos()
    print("\n--- Scraped IPO Details for All IPOs ---")
    print(json.dumps(full_scrape_result, indent=2))
