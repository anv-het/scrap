import requests
from bs4 import BeautifulSoup
import json
import re
import zlib # To potentially decompress if needed
import brotli # If 'br' (brotli) compression is used
import time
from datetime import datetime

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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br", # Explicitly request these encodings
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

        # --- DEBUGGING COMPRESSION/ENCODING ---
        print(f"  - Response Status Code: {response.status_code}")
        print(f"  - Response Headers: {response.headers}")
        
        # Check if content is truly compressed and handle manually if needed
        content_encoding = response.headers.get('Content-Encoding')
        print(f"  - Content-Encoding Header: {content_encoding}")

        # Attempt to decode JSON
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            print(f"✗ JSON decoding error from API response for {api_url}: {e}")
            print(f"✗ Raw response content (first 500 chars, as bytes): {response.content[:500]}")
            # If Content-Encoding is not handled by requests, try manual decompression
            if content_encoding == 'gzip':
                try:
                    decompressed_content = zlib.decompress(response.content, 16 + zlib.MAX_WBITS).decode('utf-8')
                    print(f"  - Attempted gzip decompression. Result (first 200 chars): {decompressed_content[:200]}")
                    data = json.loads(decompressed_content) # Try parsing decompressed
                except Exception as decompress_e:
                    print(f"  ✗ Manual gzip decompression failed: {decompress_e}")
                    print("  This might indicate the content is not actually gzip, or is corrupted.")
                    return []
            elif content_encoding == 'br':
                try:
                    decompressed_content = brotli.decompress(response.content).decode('utf-8')
                    print(f"  - Attempted brotli decompression. Result (first 200 chars): {decompressed_content[:200]}")
                    data = json.loads(decompressed_content) # Try parsing decompressed
                except Exception as decompress_e:
                    print(f"  ✗ Manual brotli decompression failed: {decompress_e}")
                    print("  This might indicate the content is not actually brotli, or is corrupted.")
                    return []
            else: # If no known compression or requests failed to auto-decompress
                print("  No known compression, or auto-decompression failed. The content might be malformed or something else.")
                return []
        # --- END DEBUGGING ---

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

def fetch_gmp_data_for_ipo(ipo_id):
    """
    Fetches GMP data for a specific IPO ID from the Investorgain API.
    Args:
        ipo_id (int): The ID of the IPO.
    Returns:
        dict: The JSON response containing 'ipoGmpData' and 'ipoGmpTable' HTML string.
              Returns None if there's an error or no data.
    """
    gmp_api_url = f"https://webnodejs.investorgain.com/cloud/ipo/ipo-gmp-read/{ipo_id}/true"
    print(f"  - Fetching GMP data for IPO ID {ipo_id} from API: {gmp_api_url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Host": "webnodejs.investorgain.com",
        "Referer": f"https://www.investorgain.com/ipo-gmp/{ipo_id}/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site"
    }
    try:
        response = requests.get(gmp_api_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # --- DEBUGGING COMPRESSION/ENCODING ---
        print(f"    - GMP Response Status Code: {response.status_code}")
        print(f"    - GMP Response Headers: {response.headers}")
        content_encoding = response.headers.get('Content-Encoding')
        print(f"    - GMP Content-Encoding Header: {content_encoding}")
        # --- END DEBUGGING ---

        try:
            data = response.json()
        except json.JSONDecodeError as e:
            print(f"  ✗ JSON decoding error from GMP API response for IPO ID {ipo_id}: {e}")
            print(f"  ✗ Raw GMP response content (first 500 chars, as bytes): {response.content[:500]}")
            # Manual decompression attempt for GMP API as well
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
                print("  No known compression for GMP API, or auto-decompression failed.")
                return None

        if data.get("msg") == 1:
            return data
        else:
            print(f"  ✗ GMP API response not as expected (msg != 1): {data}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Network error fetching GMP data for IPO ID {ipo_id}: {e}")
        return None
    except Exception as e:
        print(f"  ✗ An unexpected error occurred while fetching GMP data for IPO ID {ipo_id}: {e}")
        return None

def parse_gmp_api_data(gmp_data_array):
    """
    Parses the 'ipoGmpData' list from the GMP API response, extracting all specified fields.
    This usually contains the latest GMP information.
    Args:
        gmp_data_array (list): The list from the 'ipoGmpData' key in the API response.
    Returns:
        dict: A dictionary of all specified GMP fields from ipoGmpData[0],
              or an empty dict if no data.
    """
    gmp_json_data = {}
    if gmp_data_array and isinstance(gmp_data_array, list) and len(gmp_data_array) > 0:
        latest_gmp = gmp_data_array[0] 
        
        gmp_json_data = {
            "Seq": clean_text(str(latest_gmp.get("Seq", "N/A"))),
            "id (GMP Data)": clean_text(str(latest_gmp.get("id", "N/A"))),
            "ipo_id (GMP Data)": clean_text(str(latest_gmp.get("ipo_id", "N/A"))),
            "gmp_date": clean_text(latest_gmp.get("gmp_date", "N/A")),
            "gmp": clean_text(latest_gmp.get("gmp", "N/A")),
            "gmp_comments": clean_text(latest_gmp.get("gmp_comments", "N/A")),
            "gmp_compare_desc": clean_text(latest_gmp.get("gmp_compare_desc", "N/A")),
            "subject_to_sauda": clean_text(latest_gmp.get("subject_to_sauda", "N/A")),
            "gmp_city": clean_text(latest_gmp.get("gmp_city", "N/A")),
            "gmp_variation": clean_text(latest_gmp.get("gmp_variation", "N/A")),
            "max_ipo_price": clean_text(latest_gmp.get("max_ipo_price", "N/A")),
            "estimated_listing_price": clean_text(latest_gmp.get("estimated_listing_price", "N/A")),
            "gmp_percent_calc": clean_text(latest_gmp.get("gmp_percent_calc", "N/A")),
            "gmp_desc_other": clean_text(latest_gmp.get("gmp_desc_other", "N/A")),
            "up_down_status": clean_text(latest_gmp.get("up_down_status", "N/A")),
            "gmp_active_record_flag": clean_text(str(latest_gmp.get("gmp_active_record_flag", "N/A"))),
            "sub2": clean_text(latest_gmp.get("sub2", "N/A")),
            "est_profit": clean_text(latest_gmp.get("est_profit", "N/A")),
            "create_date": clean_text(latest_gmp.get("create_date", "N/A")),
            "create_date_gmp": clean_text(latest_gmp.get("create_date_gmp", "N/A")),
            "last_updated_gmp": clean_text(latest_gmp.get("last_updated_gmp", "N/A")),
            "last_updated": clean_text(latest_gmp.get("last_updated", "N/A")),
            "scraped_at": datetime.now().isoformat()
        }
    return gmp_json_data

def parse_gmp_trend_table(html_table_string):
    """
    Parses the HTML table string (ipoGmpTable) to extract day-wise GMP trends
    for the specified 7 columns.
    Args:
        html_table_string (str): The HTML content of the GMP trend table.
    Returns:
        list: A list of dictionaries, where each dictionary represents a row in the table.
    """
    gmp_trend_data = []
    if not html_table_string:
        return gmp_trend_data

    soup = BeautifulSoup(html_table_string, 'html.parser')
    table = soup.find('table')

    if not table:
        return gmp_trend_data

    desired_columns = [
        "GMP Date",
        "IPO Price",
        "GMP",
        "Sub2 Sauda Rate",
        "Estimated Listing Price",
        "Estimated Profit",
        "Last Updated"
    ]
    
    raw_headers_from_table = [clean_text(th.get_text()) for th in table.find('thead').find_all('th')]
    
    header_to_output_key_map = {}
    for header in raw_headers_from_table:
        if "Estimated Profit" in header:
            header_to_output_key_map[header] = "Estimated Profit"
        else:
            header_to_output_key_map[header] = header

    body_rows = table.find('tbody').find_all('tr')
    for row in body_rows:
        row_data = {}
        cells = row.find_all('td')
        
        if len(cells) >= len(desired_columns):
            for i, cell in enumerate(cells):
                if i < len(raw_headers_from_table):
                    raw_header = raw_headers_from_table[i]
                    output_key = header_to_output_key_map.get(raw_header)
                    
                    if output_key in desired_columns:
                        cell_text = clean_text(cell.get_text(separator=" ", strip=True))
                        row_data[output_key] = cell_text
            
            if all(col in row_data for col in desired_columns):
                gmp_trend_data.append(row_data)

    return gmp_trend_data

def save_to_json(data, filename="investorgain_ipo_gmp_data.json"):
    """
    Saves the scraped data to a JSON file.
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"\n✓ All Investorgain IPO GMP data saved to JSON: {filename}")
    except IOError as e:
        print(f"✗ Error saving JSON: {e}")

if __name__ == "__main__":
    print("=== Investorgain IPO GMP Data Scraper ===")
    print("This script fetches IPO IDs, then retrieves and parses all specified GMP data (latest JSON and historical table).")
    print("Output will be saved to 'investorgain_ipo_gmp_data.json'.")

    all_ipo_gmp_data = []

    ipo_list = fetch_ipo_list_from_api()

    if ipo_list:
        print(f"\nStarting GMP data scraping for {len(ipo_list)} IPOs...")
        for i, ipo_entry in enumerate(ipo_list, 1):
            ipo_id = ipo_entry.get('id')
            company_short_name = ipo_entry.get('company_short_name', 'N/A')

            if not ipo_id:
                print(f"✗ Skipping IPO entry {i}/{len(ipo_list)} ({company_short_name}) due to missing IPO ID.")
                all_ipo_gmp_data.append({
                    "IPO ID (from List API)": "N/A",
                    "Company Name (from List API)": company_short_name,
                    "Scrape Status": "Skipped (Missing IPO ID)"
                })
                continue

            print(f"\n--- Processing IPO {i}/{len(ipo_list)}: {company_short_name} (ID: {ipo_id}) ---")
            
            gmp_api_response = fetch_gmp_data_for_ipo(ipo_id)

            combined_gmp_info = {
                "IPO ID (from List API)": ipo_id,
                "Company Name (from List API)": company_short_name,
            }

            if gmp_api_response:
                latest_gmp_details = parse_gmp_api_data(gmp_api_response.get("ipoGmpData", []))
                combined_gmp_info.update(latest_gmp_details)
                
                gmp_trend_table_data = parse_gmp_trend_table(gmp_api_response.get("ipoGmpTable", ""))
                
                combined_gmp_info["GMP Trend History (Table)"] = gmp_trend_table_data 
                combined_gmp_info["Scrape Status"] = "Success"

                gmp_data_ipo_id = combined_gmp_info.get("ipo_id (GMP Data)")
                if gmp_data_ipo_id != "N/A" and str(gmp_data_ipo_id) != str(ipo_id):
                    print(f"  ⚠️ Warning: IPO ID mismatch! List API ID: {ipo_id}, GMP Data ID: {gmp_data_ipo_id}")

            else:
                print(f"  ✗ No GMP data retrieved for IPO ID {ipo_id}.")
                combined_gmp_info["Scrape Status"] = "Failed (GMP API call or data missing)"
                combined_gmp_info["GMP Trend History (Table)"] = []

            all_ipo_gmp_data.append(combined_gmp_info)
    else:
        print("\nNo IPOs fetched from the main API. Exiting GMP scraper.")

    if all_ipo_gmp_data:
        save_to_json(all_ipo_gmp_data)
        
        print("\n=== Sample Scraped GMP Data (First IPO) ===")
        if len(all_ipo_gmp_data) > 0:
            sample_gmp = all_ipo_gmp_data[0]
            for key, value in sample_gmp.items():
                if isinstance(value, list) and key == "GMP Trend History (Table)" and len(value) > 2:
                    print(f"{key}: {value[0]} ... (and {len(value)-1} more entries)")
                elif isinstance(value, str) and len(value) > 100:
                    print(f"{key}: {value[:97]}...")
                else:
                    print(f"{key}: {value}")
    else:
        print("\nNo GMP data was processed.")
    
    print("\n=== Script Complete ===")


    