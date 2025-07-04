import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime # Included for potential date parsing utility, though not directly in this specific API fetch

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
            print(f"✓ Successfully fetched {len(data['ipoList'])} IPOs from the new API.")
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

def scrape_ipo_details_table(url):
    """
    Scrapes detailed IPO issue information from the main table on an IPO detail page.
    Args:
        url (str): The URL of the IPO detail page to scrape.
    Returns:
        dict: A dictionary containing the scraped IPO details from the table.
    """
    print(f"\nAttempting to scrape table from: {url}")
    issue_details_data = {}

    # Define patterns for mapping scraped labels to desired output keys.
    detail_field_patterns_map = {
        "IPO Issue Opening Date": re.compile(r'Issue Opening Date', re.IGNORECASE),
        "IPO Issue Closing Date": re.compile(r'Issue Closing Date', re.IGNORECASE),
        "IPO Issue Price": re.compile(r'Issue Price', re.IGNORECASE),
        "DRHP Link": re.compile(r'DRHP', re.IGNORECASE),
        "RHP Link": re.compile(r'RHP', re.IGNORECASE),
        "Anchor List Link": re.compile(r'Anchor List', re.IGNORECASE),
        "Listing At": re.compile(r'Listing At|Listing On', re.IGNORECASE),
        "Retail Quota": re.compile(r'Retail Quota|Retail Allotment %', re.IGNORECASE),
        "IPO Issue Type": re.compile(r'Issue Type', re.IGNORECASE),
        "IPO Issue Size (Cr)": re.compile(r'Issue Size', re.IGNORECASE),
        "Fresh Issue (Cr)": re.compile(r'Fresh Issue', re.IGNORECASE),
        "Face Value": re.compile(r'Face Value', re.IGNORECASE),
        "Promoter Holding Pre IPO (%)": re.compile(r'Promoter Holding Pre IPO', re.IGNORECASE),
        "Promoter Holding Post IPO (%)": re.compile(r'Promoter Holding Post IPO', re.IGNORECASE),
        "Min Order Quantity (Table)": re.compile(r'Min Order Quantity|Min Application', re.IGNORECASE),
        "Lot Size (Table)": re.compile(r'Market Lot|Lot Size', re.IGNORECASE),
        "Allotment Status": re.compile(r'Allotment Status', re.IGNORECASE), # This key's value will now be the URL
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # === START OF THE if main_details_table BLOCK ===
        main_details_table = soup.find('table', class_='table table-bordered table-striped table-hover w-auto')
        
        if main_details_table:
            print("  ✓ Found main IPO details table.")
            for row in main_details_table.find_all('tr'):
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    label_element = cells[0]
                    value_element = cells[1]

                    label_text = clean_text(label_element.get_text(strip=True))
                    value = 'N/A' 

                    # 1. Prioritize 'data-title' for dates (as some dates might be hidden in text)
                    if 'data-title' in value_element.attrs and \
                       any(re.search(pattern, label_text) for pattern in [r'Issue Opening Date', r'Issue Closing Date']):
                        value = clean_text(value_element['data-title'])
                    else:
                        # 2. Check for any link within the value element
                        found_link_element = value_element.find('a', href=True)
                        if found_link_element:
                            link_href = found_link_element['href']
                            # If it's a relative URL, make it absolute
                            if link_href.startswith('/'):
                                # Base domain for Investorgain.com relative URLs
                                value = f"https://www.investorgain.com{link_href}"
                            else:
                                value = link_href
                        else:
                            # 3. Fallback to get_text() if no specific pattern matched
                            value = clean_text(value_element.get_text(strip=True))
                    
                    # Ensure that if value is an empty string after cleaning, it defaults to 'N/A'
                    if not value and value != '': # This handles cases where value might be empty string after clean_text
                        value = 'N/A'

                    for output_key, pattern in detail_field_patterns_map.items():
                        if pattern.search(label_text):
                            issue_details_data[output_key] = value
                            break # Move to the next row once a match is found for this row
        else:
            print("  ✗ Main IPO details table not found for extraction.")
        # === END OF THE if main_details_table BLOCK ===

    except requests.exceptions.RequestException as e:
        print(f"  ✗ Network error fetching {url}: {e}")
    except Exception as e:
        print(f"  ✗ Parsing error for {url}: {e}")

    # Ensure all expected keys are present, even if N/A
    for key in detail_field_patterns_map.keys():
        if key not in issue_details_data:
            issue_details_data[key] = 'N/A'
    
    return issue_details_data

def save_to_json(data, filename="all_ipo_table_data.json"):
    """
    Saves the scraped data to a JSON file.
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"\n✓ All IPO table data saved to JSON: {filename}")
    except IOError as e:
        print(f"✗ Error saving JSON: {e}")

if __name__ == "__main__":
    print("=== All IPO Table Scraper ===")
    print("This script fetches a list of current/upcoming IPOs and scrapes their detail tables.")
    print("Output will be saved to 'all_ipo_table_data.json'.")

    base_url = "https://www.investorgain.com/" 
    all_scraped_ipo_data = []

    ipo_list = fetch_ipo_list_from_api()

    if ipo_list:
        print(f"\nStarting table scraping for {len(ipo_list)} IPOs...")
        for i, ipo_entry in enumerate(ipo_list, 1):
            urlrewrite_folder_name = ipo_entry.get('urlrewrite_folder_name')
            ipo_id = ipo_entry.get('id')
            urlrewrite_folder_name_main = ipo_entry.get('urlrewrite_folder_name_main')
            company_short_name = ipo_entry.get('company_short_name', 'N/A') 

            if not urlrewrite_folder_name or not ipo_id or not urlrewrite_folder_name_main:
                print(f"✗ Skipping IPO entry {i}/{len(ipo_list)} ({company_short_name}) due to missing URL components.")
                all_scraped_ipo_data.append({
                    "IPO ID": ipo_id if ipo_id else 'N/A',
                    "API Company Name": company_short_name,
                    "Detail URL": "N/A (Skipped - Missing URL components)",
                    "Scrape Status": "Skipped (Incomplete API data for URL)"
                })
                continue

            detail_url = f"{base_url}{urlrewrite_folder_name_main}/{urlrewrite_folder_name}/{ipo_id}/"
            
            print(f"\n--- Scraping IPO {i}/{len(ipo_list)}: {company_short_name} ({detail_url}) ---")
            
            table_details = scrape_ipo_details_table(detail_url)
            
            api_info_to_keep = {
                "IPO ID": ipo_id,
                "API Company Name": company_short_name,
                "API IPO Category": ipo_entry.get('ipo_category', 'N/A'),
                "Detail URL": detail_url,
                "API Issue Size": ipo_entry.get("issue_size", "N/A"),
                "API Issue Open Date": ipo_entry.get("issue_open_dt", "N/A"),
                "API Issue End Date": ipo_entry.get("issue_end_dt", "N/A"),
                "API Listing At": ipo_entry.get("listing_at", "N/A"),
                "API IPO Status": ipo_entry.get("ipo_status", "N/A"),
            }

            combined_data = {**api_info_to_keep, **table_details}
            all_scraped_ipo_data.append(combined_data)
    else:
        print("\nNo IPOs fetched from the API. Exiting.")

    if all_scraped_ipo_data:
        save_to_json(all_scraped_ipo_data)
        
        print("\n=== Sample Scraped Data (First IPO) ===")
        if len(all_scraped_ipo_data) > 0:
            sample = all_scraped_ipo_data[0]
            for key, value in sample.items():
                display_value = str(value)
                if len(display_value) > 100:
                    display_value = display_value[:97] + "..."
                print(f"{key}: {display_value}")
    else:
        print("\nNo data was scraped.")
    
    print("\n=== Script Complete ===")

    