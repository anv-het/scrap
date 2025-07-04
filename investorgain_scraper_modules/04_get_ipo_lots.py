import requests
from bs4 import BeautifulSoup
import json
import re

def clean_text(text):
    """
    Cleans extracted text by removing extra spaces, newlines, and non-breaking spaces.
    """
    if text:
        text = text.replace('\xa0', ' ').replace('\n', ' ').strip()
        text = re.sub(r'\s+', ' ', text)
    return text

def fetch_ipo_list_from_api():
    """
    Fetches the list of IPOs from the Investorgain API (webnodejs.investorgain.com).
    This API returns 'urlrewrite_folder_name' and 'id' for URL construction.
    """
    api_url = "https://webnodejs.investorgain.com/cloud/ipo/list-read"
    print(f"Fetching IPO list from API: {api_url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        if data.get("msg") == 1 and "ipoList" in data:
            print(f"✓ Successfully fetched {len(data['ipoList'])} IPOs from the API.")
            return data["ipoList"]
        else:
            print(f"✗ API response not as expected (msg != 1 or 'ipoList' missing): {data}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"✗ Network error fetching IPO list from API: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"✗ JSON decoding error from API response: {e}")
        return []
    except Exception as e:
        print(f"✗ An unexpected error occurred while fetching IPO list: {e}")
        return []


def scrape_ipo_lots_table(url):
    """
    Scrapes the "IPO Lots" table from an IPO detail page.
    Args:
        url (str): The URL of the IPO detail page to scrape.
    Returns:
        dict: A dictionary containing the scraped IPO lot details.
    """
    print(f"\nAttempting to scrape 'IPO Lots' table from: {url}")
    ipo_lots_data = {}

    # Define patterns for mapping scraped labels to desired output keys.
    # Added "Individual Investor" and "Min HNI Lots"
    lot_field_patterns_map = {
        "Lot Issue Price": re.compile(r'Issue Price', re.IGNORECASE),
        "Lot Market Lot": re.compile(r'Market Lot', re.IGNORECASE),
        "Lot Individual Investor": re.compile(r'Individual Investor', re.IGNORECASE), # New field
        "Lot Min HNI Lots": re.compile(r'Min HNI Lots', re.IGNORECASE),             # New field
        "Lot Min Small HNI Lots (2-10 Lakh)": re.compile(r'Min Small HNI Lots\(2-10 Lakh\)', re.IGNORECASE),
        "Lot Min Big HNI Lots (10+ Lakh)": re.compile(r'Min Big HNI Lots\(10\+ Lakh\)', re.IGNORECASE),
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        ipo_lots_table = None
        # Robustly find the h2 tag that contains "IPO Lots" in its text content
        for h2_tag in soup.find_all('h2'):
            h2_text_content = clean_text(h2_tag.get_text())
            if re.search(r'IPO.*Lots', h2_text_content, re.IGNORECASE):
                # If found, the desired table is its immediate next sibling with the specified class
                ipo_lots_table = h2_tag.find_next_sibling('table', class_='table table-bordered table-striped table-hover w-auto')
                if ipo_lots_table: # Ensure the table was actually found
                    break # Exit the loop once the correct h2 and table are located
        
        if ipo_lots_table:
            print("  ✓ Found 'IPO Lots' table.")
            # Iterate through table rows to extract data
            for row in ipo_lots_table.find_all('tr'):
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2: # Ensure there are at least two cells (label and value)
                    label_element = cells[0]
                    value_element = cells[1]

                    label_text = clean_text(label_element.get_text(strip=True))
                    value = clean_text(value_element.get_text(strip=True))
                    
                    # Default to 'N/A' if the value is empty after cleaning
                    if not value and value != '': 
                        value = 'N/A'

                    # Map the scraped label to our desired output key
                    for output_key, pattern in lot_field_patterns_map.items():
                        if pattern.search(label_text):
                            ipo_lots_data[output_key] = value
                            break # Move to the next row once a match is found for this row
        else:
            print("  ✗ 'IPO Lots' table not found for extraction.")

    except requests.exceptions.RequestException as e:
        print(f"  ✗ Network error fetching {url}: {e}")
    except Exception as e:
        print(f"  ✗ Parsing error for {url}: {e}")

    # Ensure all expected keys are present in the final output, defaulting to 'N/A' if not found
    for key in lot_field_patterns_map.keys():
        if key not in ipo_lots_data:
            ipo_lots_data[key] = 'N/A'
    
    return ipo_lots_data



def save_to_json(data, filename="ipo_lots_data.json"):
    """
    Saves the scraped data to a JSON file.
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"\n✓ IPO Lots data saved to JSON: {filename}")
    except IOError as e:
        print(f"✗ Error saving JSON: {e}")

def save_to_json(data, filename="investorgain_lots_ipo_data.json"):
    """
    Saves the scraped data to a JSON file.
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"\n✓ All Investorgain IPO data saved to JSON: {filename}")
    except IOError as e:
        print(f"✗ Error saving JSON: {e}")

if __name__ == "__main__":
    print("=== Investorgain All IPO Data Scraper ===")
    print("This script fetches a list of current/upcoming IPOs and scrapes their main details and lot size tables.")
    print("Output will be saved to 'investorgain_all_ipo_data.json'.")

    base_url = "https://www.investorgain.com/" 
    all_combined_ipo_data = []

    # Step 1: Fetch IPO list from the API
    ipo_list = fetch_ipo_list_from_api()

    if ipo_list:
        print(f"\nStarting detailed scraping for {len(ipo_list)} IPOs...")
        for i, ipo_entry in enumerate(ipo_list, 1):
            urlrewrite_folder_name = ipo_entry.get('urlrewrite_folder_name')
            ipo_id = ipo_entry.get('id')
            urlrewrite_folder_name_main = ipo_entry.get('urlrewrite_folder_name_main')
            company_short_name = ipo_entry.get('company_short_name', 'N/A') 

            if not urlrewrite_folder_name or not ipo_id or not urlrewrite_folder_name_main:
                print(f"✗ Skipping IPO entry {i}/{len(ipo_list)} ({company_short_name}) due to missing URL components from API.")
                all_combined_ipo_data.append({
                    "IPO ID": ipo_id if ipo_id else 'N/A',
                    "API Company Name": company_short_name,
                    "Detail URL": "N/A (Skipped - Missing URL components)",
                    "Scrape Status": "Skipped (Incomplete API data for URL)"
                })
                continue

            detail_url = f"{base_url}{urlrewrite_folder_name_main}/{urlrewrite_folder_name}/{ipo_id}/"
            
            print(f"\n--- Processing IPO {i}/{len(ipo_list)}: {company_short_name} ---")
            print(f"  Detail URL: {detail_url}")
            
            # Step 2: Scrape the main detailed table from the webpage
            # main_details = scrape_ipo_details_table(detail_url)
            
            # Step 3: Scrape the IPO Lots table from the webpage
            lots_details = scrape_ipo_lots_table(detail_url)
            
            # Step 4: Combine API data with scraped table data
            api_info_to_keep = {
                "IPO ID": ipo_id,
                "API Company Name": company_short_name,
                "API IPO Category": ipo_entry.get('ipo_category', 'N/A'),
                "API Issue Size": ipo_entry.get("issue_size", "N/A"),
                "API Issue Open Date": ipo_entry.get("issue_open_dt", "N/A"),
                "API Issue End Date": ipo_entry.get("issue_end_dt", "N/A"),
                "API Listing At": ipo_entry.get("listing_at", "N/A"),
                "API IPO Status": ipo_entry.get("ipo_status", "N/A"),
                "Detail URL": detail_url # Keep the constructed URL for reference
            }

            # Merge all dictionaries. Later dictionaries' keys will overwrite earlier ones if duplicates.
            # We use distinct keys for main table vs. lots table to avoid collisions.
            combined_data = {**api_info_to_keep, **lots_details}
            all_combined_ipo_data.append(combined_data)
    else:
        print("\nNo IPOs fetched from the API. Exiting.")

    # Step 5: Save all collected data to a JSON file
    if all_combined_ipo_data:
        save_to_json(all_combined_ipo_data)
        
        # Optional: Print a summary of the first scraped IPO for verification
        print("\n=== Sample Combined Scraped Data (First IPO) ===")
        if len(all_combined_ipo_data) > 0:
            sample = all_combined_ipo_data[0]
            for key, value in sample.items():
                display_value = str(value)
                if len(display_value) > 100: # Shorten long strings for console output
                    display_value = display_value[:97] + "..."
                print(f"{key}: {display_value}")
    else:
        print("\nNo data was scraped.")
    
    #print save data in to file name 
    print("\n ====== save data in to file name ====== ")
    save_to_json(all_combined_ipo_data, "investorgain_lots_ipo_data.json")
    print("\n=== Script Complete ===")

