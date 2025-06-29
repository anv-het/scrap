import requests
from bs4 import BeautifulSoup
import json
import re
import zlib
import brotli

def clean_text(text):
    """
    Cleans extracted text by removing extra spaces, newlines, non-breaking spaces,
    and common symbols like Rupee sign, commas, and percentage/ratio indicators.
    """
    if text:
        text = text.replace('\xa0', ' ').replace('\n', ' ').strip()
        text = re.sub(r'\s+', ' ', text) # Replace multiple spaces with a single space
        text = text.replace('&#8377;', '').replace('₹', '').replace(',', '').replace('x', '').replace('%', '')
    return text

def convert_to_int(value):
    """Converts a cleaned string to an integer, returning None if conversion fails."""
    try:
        # Convert to float first to handle cases like "1.00" shares
        return int(float(value)) if value is not None and value.strip() else None
    except (ValueError, TypeError):
        return None

def convert_to_float(value):
    """Converts a cleaned string to a float, returning None if conversion fails."""
    try:
        return float(value) if value is not None and value.strip() else None
    except (ValueError, TypeError):
        return None

# ( ... keep fetch_ipo_list_from_api and fetch_ipo_subscription_data unchanged ... )

# --- REFINING ONLY THIS FUNCTION ---
def parse_ipo_share_allocation(html_string):
    """
    Parses the 'listItemsHTML' to extract IPO Share Allocation data.
    Handles various formats of category names and ensures robust data extraction.
    """
    allocation_data = []
    if not html_string:
        return allocation_data

    soup = BeautifulSoup(html_string, 'html.parser')
    list_items = soup.find_all('li')

    # Regex to capture different category name formats
    # Group 1: Category Name (e.g., "Qualified Institutional Buyers", "Small NII (SNII- Bid below ₹10L)")
    # Group 2: Shares allocated (e.g., "1,31,09,755.00 Shares")
    # Group 3: Percentage (e.g., "28.37")
    # This regex is more permissive for the category name to handle nested parentheses.
    # It aims to capture everything before the colon as the category.
    # The shares part captures digits, commas, periods, and optional " Shares".
    # The percentage part captures digits and periods.
    
    # Updated regex for more robust matching of category names and values
    allocation_regex = re.compile(
        r'(.+?):\s*([\d,\.]+\s*Shares?)\s*\(([\d\.]+)%\)'
    )

    for item in list_items:
        text = item.get_text().strip() # Get raw text, then clean after matching
        
        match = allocation_regex.search(text)
        if match:
            raw_category = match.group(1).strip()
            raw_shares = match.group(2).strip()
            raw_percentage = match.group(3).strip()

            category = clean_text(raw_category)
            shares_allocated = convert_to_int(clean_text(raw_shares.replace(' Shares', '')))
            allocation_pct = convert_to_float(clean_text(raw_percentage))
            
            allocation_data.append({
                "category": category,
                "shares_allocated": shares_allocated,
                "allocation_pct": allocation_pct
            })
        else:
            print(f"  Warning: Could not parse list item for share allocation (regex mismatch): '{text}'") # Log unparsed items for debugging
            # If a list item doesn't match the regex, include its raw text for inspection
            allocation_data.append({
                "category": clean_text(text),
                "shares_allocated": None,
                "allocation_pct": None,
                "parsing_error": True
            })

    return allocation_data

# ( ... keep parse_ipo_bidding_data_json, parse_ipo_daywise_subscription_table,
#        parse_ipo_shares_bid_amount_table, save_to_json, and __main__ block unchanged ... )

# The complete script would look like this (replace existing functions):

import requests
from bs4 import BeautifulSoup
import json
import re
import zlib # For gzip decompression
import brotli # For brotli decompression (install with: pip install brotli)

def clean_text(text):
    """
    Cleans extracted text by removing extra spaces, newlines, non-breaking spaces,
    and common symbols like Rupee sign, commas, and percentage/ratio indicators.
    """
    if text:
        text = text.replace('\xa0', ' ').replace('\n', ' ').strip()
        text = re.sub(r'\s+', ' ', text) # Replace multiple spaces with a single space
        text = text.replace('&#8377;', '').replace('₹', '').replace(',', '').replace('x', '').replace('%', '')
    return text

def convert_to_int(value):
    """Converts a cleaned string to an integer, returning None if conversion fails."""
    try:
        # Convert to float first to handle cases like "1.00" shares
        return int(float(value)) if value is not None and value.strip() else None
    except (ValueError, TypeError):
        return None

def convert_to_float(value):
    """Converts a cleaned string to a float, returning None if conversion fails."""
    try:
        return float(value) if value is not None and value.strip() else None
    except (ValueError, TypeError):
        return None

def fetch_ipo_list_from_api():
    """
    Fetches the list of IPOs from the Investorgain API (webnodejs.investorgain.com).
    This API returns 'urlrewrite_folder_name' and 'id' for URL construction.
    """
    api_url = "https://webnodejs.investorgain.com/cloud/ipo/list-read"
    print(f"Fetching IPO list from API: {api_url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Host": "webnodejs.investorgain.com",
        "Referer": "https://www.investorgain.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site"
    }
    try:
        response = requests.get(api_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        print(f"  - Response Status Code: {response.status_code}")
        print(f"  - Response Headers: {response.headers.get('Content-Encoding')}")

        try:
            data = response.json()
        except json.JSONDecodeError as e:
            print(f"✗ JSON decoding error from API response for {api_url}: {e}")
            print(f"✗ Raw response content (first 500 chars, as bytes): {response.content[:500]}")
            
            content_encoding = response.headers.get('Content-Encoding')
            if content_encoding == 'gzip':
                try:
                    decompressed_content = zlib.decompress(response.content, 16 + zlib.MAX_WBITS).decode('utf-8')
                    print(f"  - Attempted gzip decompression. Result (first 200 chars): {decompressed_content[:200]}")
                    data = json.loads(decompressed_content)
                except Exception as decompress_e:
                    print(f"  ✗ Manual gzip decompression failed: {decompress_e}")
                    return []
            elif content_encoding == 'br':
                try:
                    decompressed_content = brotli.decompress(response.content).decode('utf-8')
                    print(f"  - Attempted brotli decompression. Result (first 200 chars): {decompressed_content[:200]}")
                    data = json.loads(decompressed_content)
                except Exception as decompress_e:
                    print(f"  ✗ Manual brotli decompression failed: {decompress_e}")
                    return []
            else:
                print("  No known compression, or auto-decompression failed.")
                return []

        if data.get("msg") == 1 and "ipoList" in data:
            print(f"✓ Successfully fetched {len(data['ipoList'])} IPOs from the API.")
            return data["ipoList"]
        else:
            print(f"✗ API response not as expected (msg != 1 or 'ipoList' missing): {data}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"✗ Network error fetching IPO list from API: {e}")
        return []
    except Exception as e:
        print(f"✗ An unexpected error occurred while fetching IPO list: {e}")
        return []

def fetch_ipo_subscription_data(ipo_id):
    """
    Fetches IPO subscription data for a specific IPO ID from the Investorgain API.
    Args:
        ipo_id (int): The ID of the IPO.
    Returns:
        dict: The JSON response containing 'data' with 'ipoBiddingData', 'metaTitle', etc.,
              and 'sResultIPOBidding' HTML string. Returns None if there's an error or no data.
    """
    subscription_api_url = f"https://webnodejs.investorgain.com/cloud/ipo/ipo-subscription-read/{ipo_id}"
    print(f"  - Fetching Subscription data for IPO ID {ipo_id} from API: {subscription_api_url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Host": "webnodejs.investorgain.com",
        "Referer": f"https://www.investorgain.com/ipo-subscription/{ipo_id}/", # Referer should match
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site"
    }
    try:
        response = requests.get(subscription_api_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        print(f"    - Sub. Response Status Code: {response.status_code}")
        print(f"    - Sub. Response Headers: {response.headers.get('Content-Encoding')}")

        try:
            data = response.json()
        except json.JSONDecodeError as e:
            print(f"  ✗ JSON decoding error from Subscription API response for IPO ID {ipo_id}: {e}")
            print(f"  ✗ Raw Subscription response content (first 500 chars, as bytes): {response.content[:500]}")
            
            content_encoding = response.headers.get('Content-Encoding')
            if content_encoding == 'gzip':
                try:
                    decompressed_content = zlib.decompress(response.content, 16 + zlib.MAX_WBITS).decode('utf-8')
                    print(f"    - Attempted gzip decompression. Result (first 200 chars): {decompressed_content[:200]}")
                    data = json.loads(decompressed_content)
                except Exception as decompress_e:
                    print(f"    ✗ Manual gzip decompression failed: {decompress_e}")
                    return None
            elif content_encoding == 'br':
                try:
                    decompressed_content = brotli.decompress(response.content).decode('utf-8')
                    print(f"    - Attempted brotli decompression. Result (first 200 chars): {decompressed_content[:200]}")
                    data = json.loads(decompressed_content)
                except Exception as decompress_e:
                    print(f"    ✗ Manual brotli decompression failed: {decompress_e}")
                    return None
            else:
                print("  No known compression for Subscription API, or auto-decompression failed.")
                return None

        if data.get("msg") == 1:
            return data
        else:
            print(f"  ✗ Subscription API response not as expected (msg != 1): {data}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Network error fetching Subscription data for IPO ID {ipo_id}: {e}")
        return None
    except Exception as e:
        print(f"  ✗ An unexpected error occurred while fetching Subscription data for IPO ID {ipo_id}: {e}")
        return None

def parse_ipo_bidding_data_json(bidding_data_array):
    """
    Parses the 'ipoBiddingData' list from the Subscription API response,
    extracting all specified fields.
    """
    parsed_data = []
    if not bidding_data_array:
        return parsed_data

    for entry in bidding_data_array:
        parsed_entry = {
            "Seq": convert_to_int(clean_text(str(entry.get("Seq", "N/A")))),
            "id (Subscription Data)": convert_to_int(clean_text(str(entry.get("id", "N/A")))),
            "tsb_ipo_id": convert_to_int(clean_text(str(entry.get("tsb_ipo_id", "N/A")))),
            "cor_id": convert_to_int(clean_text(str(entry.get("cor_id", "N/A")))),
            "bid_date": clean_text(entry.get("bid_date", "N/A")),
            "qib_offered": convert_to_int(clean_text(entry.get("qib_offered", "N/A"))),
            "nii_offered": convert_to_int(clean_text(entry.get("nii_offered", "N/A"))),
            "nii_offered_big": convert_to_int(clean_text(entry.get("nii_offered_big", "N/A"))),
            "nii_offered_small": convert_to_int(clean_text(entry.get("nii_offered_small", "N/A"))),
            "rii_offered": convert_to_int(clean_text(entry.get("rii_offered", "N/A"))),
            "emp_offered": convert_to_int(clean_text(entry.get("emp_offered", "N/A"))),
            "other_offered": convert_to_int(clean_text(entry.get("other_offered", "N/A"))),
            "total_offered": convert_to_int(clean_text(entry.get("total_offered", "N/A"))),
            "qib_shares_bid_for": convert_to_int(clean_text(entry.get("qib_shares_bid_for", "N/A"))),
            "nii_shares_bid_for": convert_to_int(clean_text(entry.get("nii_shares_bid_for", "N/A"))),
            "nii_shares_bid_for_big": convert_to_int(clean_text(entry.get("nii_shares_bid_for_big", "N/A"))),
            "nii_shares_bid_for_small": convert_to_int(clean_text(entry.get("nii_shares_bid_for_small", "N/A"))),
            "rii_shares_bid_for": convert_to_int(clean_text(entry.get("rii_shares_bid_for", "N/A"))),
            "emp_shares_bid_for": convert_to_int(clean_text(entry.get("emp_shares_bid_for", "N/A"))),
            "other_shares_bid_for": convert_to_int(clean_text(entry.get("other_shares_bid_for", "N/A"))),
            "total_shares_bid_for": convert_to_int(clean_text(entry.get("total_shares_bid_for", "N/A"))),
            "qib_bid_amt": convert_to_float(clean_text(entry.get("qib_bid_amt", "N/A"))),
            "nii_bid_amt": convert_to_float(clean_text(entry.get("nii_bid_amt", "N/A"))),
            "nii_bid_amt_big": convert_to_float(clean_text(entry.get("nii_bid_amt_big", "N/A"))),
            "nii_bid_amt_small": convert_to_float(clean_text(entry.get("nii_bid_amt_small", "N/A"))),
            "rii_bid_amt": convert_to_float(clean_text(entry.get("rii_bid_amt", "N/A"))),
            "emp_bid_amt": convert_to_float(clean_text(entry.get("emp_bid_amt", "N/A"))),
            "other_bid_amt": convert_to_float(clean_text(entry.get("other_bid_amt", "N/A"))),
            "total_bid_amt": convert_to_float(clean_text(entry.get("total_bid_amt", "N/A"))),
            "qib": convert_to_float(clean_text(entry.get("qib", "N/A"))),
            "nii": convert_to_float(clean_text(entry.get("nii", "N/A"))),
            "nii_big": convert_to_float(clean_text(entry.get("nii_big", "N/A"))),
            "nii_small": convert_to_float(clean_text(entry.get("nii_small", "N/A"))),
            "rii": convert_to_float(clean_text(entry.get("rii", "N/A"))),
            "emp": convert_to_float(clean_text(entry.get("emp", "N/A"))),
            "other": convert_to_float(clean_text(entry.get("other", "N/A"))),
            "total": convert_to_float(clean_text(entry.get("total", "N/A"))),
            "cor_date_added": clean_text(entry.get("cor_date_added", "N/A")),
            "create_date": clean_text(entry.get("create_date", "N/A")),
            "ipo_category_desc": clean_text(entry.get("ipo_category_desc", "N/A")),
            "listing_at": clean_text(entry.get("listing_at", "N/A")),
            "company_short_name": clean_text(entry.get("company_short_name", "N/A"))
        }
        parsed_data.append(parsed_entry)
    return parsed_data

# --- MODIFIED parse_ipo_share_allocation FUNCTION ---
def parse_ipo_share_allocation(html_string):
    """
    Parses the 'listItemsHTML' to extract IPO Share Allocation data.
    Handles various formats of category names and ensures robust data extraction.
    """
    allocation_data = []
    if not html_string:
        return allocation_data

    soup = BeautifulSoup(html_string, 'html.parser')
    list_items = soup.find_all('li')

    # Regex to capture different category name formats
    # Group 1: Category Name (e.g., "Qualified Institutional Buyers", "Small NII (SNII- Bid below ₹10L)")
    # Group 2: Shares allocated (e.g., "1,31,09,755.00 Shares")
    # Group 3: Percentage (e.g., "28.37")
    
    # This regex is designed to be flexible for the category name and optional 'Shares' word.
    allocation_regex = re.compile(
        r'(.+?):\s*([\d,\.]+\s*(?:Shares)?)\s*\(([\d\.]+)\%\)'
    )

    for item in list_items:
        text = item.get_text().strip() # Get raw text for regex matching

        match = allocation_regex.search(text)
        if match:
            raw_category = match.group(1).strip()
            raw_shares = match.group(2).strip()
            raw_percentage = match.group(3).strip()

            category = clean_text(raw_category)
            shares_allocated = convert_to_int(clean_text(raw_shares.replace(' Shares', '')))
            allocation_pct = convert_to_float(clean_text(raw_percentage))
            
            allocation_data.append({
                "category": category,
                "shares_allocated": shares_allocated,
                "allocation_pct": allocation_pct
            })
        else:
            print(f"  Warning: Could not parse list item for share allocation (regex mismatch): '{text}'")
            # If a list item doesn't match, include its raw text for inspection
            allocation_data.append({
                "category": clean_text(text),
                "shares_allocated": None,
                "allocation_pct": None,
                "parsing_error": True # Flag this entry for review
            })

    return allocation_data


def parse_ipo_daywise_subscription_table(html_table_string):
    """
    Parses the HTML table string from 'sResultIPOBidding' for IPO Day-wise Subscription.
    """
    daywise_data = []
    if not html_table_string:
        return daywise_data

    soup = BeautifulSoup(html_table_string, 'html.parser')
    # Find the table by its caption or a unique th/class if needed
    table = soup.find('table', caption="IPO Bidding Live Updates from BSE, NSE")
    if not table:
        table = soup.find('table', class_='table-striped') # Fallback if caption not found
        if not table:
            return daywise_data

    headers = [clean_text(th.get_text()) for th in table.find('thead').find_all('th')]
    
    header_mapping = {
        'Day': 'day_number',
        'Bid Date': 'date_time', 
        'QIB': 'qib_ratio',
        'NII': 'nii_ratio',
        'SNII (Below ₹10L)': 'snii_ratio',
        'SNII': 'snii_ratio',
        'BNII (Above ₹10L)': 'bnii_ratio',
        'BNII': 'bnii_ratio',
        'RII': 'rii_ratio',
        'Retail': 'rii_ratio',
        'Total': 'total_ratio'
    }

    output_keys = []
    for h in headers:
        found_match = False
        for mapped_h, out_key in header_mapping.items():
            if mapped_h in h:
                output_keys.append(out_key)
                found_match = True
                break
        if not found_match:
            output_keys.append(clean_text(h).lower().replace(' ', '_'))

    body_rows = table.find('tbody').find_all('tr')
    for row in body_rows:
        row_data = {}
        cells = row.find_all('td')
        if len(cells) < len(output_keys):
            continue

        for i, cell in enumerate(cells):
            if i < len(output_keys):
                key = output_keys[i]
                value = clean_text(cell.get_text())
                
                if key == 'day_number':
                    row_data[key] = convert_to_int(value)
                elif '_ratio' in key:
                    row_data[key] = convert_to_float(value)
                else:
                    row_data[key] = value
        daywise_data.append(row_data)
    return daywise_data


def parse_ipo_shares_bid_amount_table(html_table_string):
    """
    Parses the HTML table string from 'sResultIPOBidding' for IPO Shares Bid Amount.
    This table usually appears after the Day-wise Subscription table.
    """
    bid_amount_data = []
    if not html_table_string:
        return bid_amount_data

    soup = BeautifulSoup(html_table_string, 'html.parser')
    
    target_table = None
    all_tables = soup.find_all('table')
    for table in all_tables:
        headers = [clean_text(th.get_text()) for th in table.find('thead').find_all('th')] if table.find('thead') else []
        if 'Category' in headers and 'Shares Offered' in headers and 'Shares Bid' in headers and any('Amount' in h for h in headers):
            target_table = table
            break

    if not target_table:
        return bid_amount_data

    headers = [clean_text(th.get_text()) for th in target_table.find('thead').find_all('th')]

    header_mapping = {
        'Category': 'category',
        'Shares Offered': 'shares_offered',
        'Shares Bid': 'shares_bid',
        'Amount (Cr.)': 'bid_amount_cr',
        'Amount (Cr)': 'bid_amount_cr'
    }

    output_keys = []
    for h in headers:
        found_match = False
        for mapped_h, out_key in header_mapping.items():
            if mapped_h in h:
                output_keys.append(out_key)
                found_match = True
                break
        if not found_match:
            output_keys.append(clean_text(h).lower().replace(' ', '_'))

    body_rows = target_table.find('tbody').find_all('tr')
    for row in body_rows:
        row_data = {}
        cells = row.find_all('td')
        if len(cells) < len(output_keys):
            continue

        for i, cell in enumerate(cells):
            if i < len(output_keys):
                key = output_keys[i]
                value = clean_text(cell.get_text())

                if key in ['shares_offered', 'shares_bid']:
                    row_data[key] = convert_to_int(value)
                elif key == 'bid_amount_cr':
                    row_data[key] = convert_to_float(value)
                else:
                    row_data[key] = value
        bid_amount_data.append(row_data)
    return bid_amount_data


def save_to_json(data, filename="investorgain_ipo_subscription_data.json"):
    """
    Saves the scraped data to a JSON file.
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"\n✓ All Investorgain IPO Subscription data saved to JSON: {filename}")
    except IOError as e:
        print(f"✗ Error saving JSON: {e}")

if __name__ == "__main__":
    print("=== Investorgain IPO Subscription Data Scraper ===")
    print("This script fetches IPO IDs, then retrieves and parses all specified subscription data.")
    print("Output will be saved to 'investorgain_ipo_subscription_data.json'.")

    all_ipo_subscription_data = []

    ipo_list = fetch_ipo_list_from_api()

    if ipo_list:
        print(f"\nStarting Subscription data scraping for {len(ipo_list)} IPOs...")
        for i, ipo_entry in enumerate(ipo_list, 1):
            ipo_id = ipo_entry.get('id')
            company_short_name = ipo_entry.get('company_short_name', 'N/A')

            if not ipo_id:
                print(f"✗ Skipping IPO entry {i}/{len(ipo_list)} ({company_short_name}) due to missing IPO ID.")
                all_ipo_subscription_data.append({
                    "IPO ID (from List API)": "N/A",
                    "Company Name (from List API)": company_short_name,
                    "Scrape Status": "Skipped (Missing IPO ID)"
                })
                continue

            print(f"\n--- Processing IPO {i}/{len(ipo_list)}: {company_short_name} (ID: {ipo_id}) ---")
            
            subscription_api_response = fetch_ipo_subscription_data(ipo_id)

            combined_subscription_info = {
                "IPO ID (from List API)": ipo_id,
                "Company Name (from List API)": company_short_name,
            }

            if subscription_api_response and subscription_api_response.get('data'):
                combined_subscription_info["IPO Bidding History (JSON)"] = parse_ipo_bidding_data_json(
                    subscription_api_response['data'].get("ipoBiddingData", [])
                )

                data_section = subscription_api_response['data']
                combined_subscription_info["metaTitle"] = clean_text(data_section.get("metaTitle", "N/A"))
                combined_subscription_info["pageTitle"] = clean_text(data_section.get("pageTitle", "N/A"))
                combined_subscription_info["metaDesc"] = clean_text(data_section.get("metaDesc", "N/A"))
                
                combined_subscription_info["cacheKey"] = clean_text(subscription_api_response.get("cacheKey", "N/A"))
                combined_subscription_info["currentTime"] = clean_text(subscription_api_response.get("currentTime", "N/A"))


                html_list_items = data_section.get("listItemsHTML", "")
                combined_subscription_info["IPO Share Allocation"] = parse_ipo_share_allocation(html_list_items)

                html_s_result = data_section.get("sResultIPOBidding", "")
                combined_subscription_info["IPO Daywise Subscription (Table)"] = parse_ipo_daywise_subscription_table(html_s_result)
                combined_subscription_info["IPO Shares Bid Amount (Table)"] = parse_ipo_shares_bid_amount_table(html_s_result)

                combined_subscription_info["Scrape Status"] = "Success"

                if combined_subscription_info["IPO Bidding History (JSON)"]:
                    bidding_ipo_id = combined_subscription_info["IPO Bidding History (JSON)"][0].get("tsb_ipo_id")
                    if bidding_ipo_id != None and str(bidding_ipo_id) != str(ipo_id):
                        print(f"  ⚠️ Warning: IPO ID mismatch in subscription data! List API ID: {ipo_id}, Bidding Data tsb_ipo_id: {bidding_ipo_id}")

            else:
                print(f"  ✗ No Subscription data retrieved or 'data' key missing for IPO ID {ipo_id}.")
                combined_subscription_info["Scrape Status"] = "Failed (Subscription API call or data missing)"
                combined_subscription_info["IPO Bidding History (JSON)"] = []
                combined_subscription_info["IPO Share Allocation"] = []
                combined_subscription_info["IPO Daywise Subscription (Table)"] = []
                combined_subscription_info["IPO Shares Bid Amount (Table)"] = []


            all_ipo_subscription_data.append(combined_subscription_info)
    else:
        print("\nNo IPOs fetched from the main API. Exiting Subscription scraper.")

    if all_ipo_subscription_data:
        save_to_json(all_ipo_subscription_data)
        
        print("\n=== Sample Scraped Subscription Data (First IPO) ===")
        if len(all_ipo_subscription_data) > 0:
            sample_sub = all_ipo_subscription_data[0]
            for key, value in sample_sub.items():
                if isinstance(value, list) and len(value) > 2:
                    print(f"{key}: {value[0]} ... (and {len(value)-1} more entries)")
                elif isinstance(value, str) and len(value) > 100:
                    print(f"{key}: {value[:97]}...")
                else:
                    print(f"{key}: {value}")
    else:
        print("\nNo Subscription data was processed.")
    
    print("\n=== Script Complete ===")

    