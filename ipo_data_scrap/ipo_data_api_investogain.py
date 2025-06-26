# import requests
# import json
# import time
# from bs4 import BeautifulSoup
# import re # For more precise regex cleaning if needed

# def fetch_and_clean_data(api_name, url, expected_fields):
#     """
#     Fetches data from a given API, cleans HTML tags from specified fields,
#     and returns a list of dictionaries.
#     """
#     headers = {
#         "Accept": "application/json",
#         "Origin": "https://www.investorgain.com",
#         "Referer": "https://www.investorgain.com/",
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
#     }

#     print(f"Fetching data for: {api_name} from {url}")
#     try:
#         response = requests.get(url, headers=headers, timeout=10)
#         response.raise_for_status() # Raise an exception for bad status codes

#         data = response.json()
#         report_data = data.get("reportTableData", [])

#         cleaned_records = []
#         for record in report_data:
#             cleaned_record = {}
#             for field in expected_fields:
#                 value = record.get(field, "")
#                 if isinstance(value, str):
#                     # Use BeautifulSoup to strip HTML tags and get clean text
#                     soup = BeautifulSoup(value, 'html.parser')
#                     clean_value = soup.get_text(separator=' ', strip=True)

#                     # Further clean specific fields for better numerical or date parsing
#                     if field in ["GMP", "Est Listing", "IPO Size"]:
#                         clean_value = clean_value.replace('&#8377;', '').replace(' (', ' (').strip()
#                         # Remove percentage signs for numerical processing later if needed
#                         clean_value = re.sub(r'\(.*?\%\)', '', clean_value).strip()
#                     elif field in ["Sub"]:
#                         clean_value = clean_value.replace('x', '').strip()

#                     cleaned_record[field.replace('~', '')] = clean_value # Remove '~' from field names
#                 else:
#                     cleaned_record[field.replace('~', '')] = value
#             cleaned_records.append(cleaned_record)
        
#         print(f"Successfully fetched {len(cleaned_records)} records for {api_name}.")
#         return cleaned_records

#     except requests.exceptions.RequestException as e:
#         print(f"Error fetching {api_name}: {e}")
#         return []
#     except json.JSONDecodeError as e:
#         print(f"Error decoding JSON for {api_name}: {e}")
#         return []
#     except Exception as e:
#         print(f"An unexpected error occurred for {api_name}: {e}")
#         return []

# def main():
#     all_ipo_data = {
#         "gmp_details": {},
#         "subscription_and_performance": {},
#         "ipo_calendar_events": []
#     }

#     # GMP Details APIs
#     gmp_fields = [
#         "~orderby1", "Name", "GMP", "Fire Rating", "Sub", "Price",
#         "Est Listing", "IPO Size", "Lot", "~P/E", "~id", "Open", "Close",
#         "BoA Dt", "Listing", "~Srt_Open", "~Srt_Close", "~Srt_BoA_Dt",
#         "~Str_Listing", "~urlrewrite_folder_name", "GMP Updated",
#         "~Display_Order", "~Highlight_Row", "~IPO_Category"
#     ]

#     all_ipo_data["gmp_details"]["all_gmp"] = fetch_and_clean_data(
#         "All IPO GMP",
#         "https://webnodejs.investorgain.com/cloud/report/data-read/331/1/6/2025/2025-26/0/all?search=&v=23-18",
#         gmp_fields
#     )
#     time.sleep(1) # Be polite, add a small delay

#     all_ipo_data["gmp_details"]["live_mainboard_gmp"] = fetch_and_clean_data(
#         "Live Mainboard GMP",
#         "https://webnodejs.investorgain.com/cloud/report/data-read/331/1/6/2025/2025-26/0/ipo?search=&v=23-49",
#         gmp_fields
#     )
#     time.sleep(1)

#     all_ipo_data["gmp_details"]["live_sme_gmp"] = fetch_and_clean_data(
#         "Live SME GMP",
#         "https://webnodejs.investorgain.com/cloud/report/data-read/331/1/6/2025/2025-26/0/sme?search=&v=23-18",
#         gmp_fields
#     )
#     time.sleep(1)

#     all_ipo_data["gmp_details"]["current_upcoming_gmp"] = fetch_and_clean_data(
#         "Current & Upcoming IPO GMP",
#         "https://webnodejs.investorgain.com/cloud/report/data-read/331/1/6/2025/2025-26/0/current?search=&v=23-49",
#         gmp_fields
#     )
#     time.sleep(1)

#     all_ipo_data["gmp_details"]["closed_ipo_gmp"] = fetch_and_clean_data(
#         "Closed IPO GMP",
#         "https://webnodejs.investorgain.com/cloud/report/data-read/331/1/6/2025/2025-26/0/close?search=&v=23-49",
#         gmp_fields
#     )
#     time.sleep(1)

#     all_ipo_data["gmp_details"]["listed_ipo_gmp"] = fetch_and_clean_data(
#         "Listed IPO GMP",
#         "https://webnodejs.investorgain.com/cloud/report/data-read/331/1/6/2025/2025-26/0/listed?search=&v=23-49",
#         gmp_fields
#     )
#     time.sleep(1)

#     # Subscription and Performance APIs
#     subscription_fields = [
#         "~idobid", "~end_dt", "Name", "Total", "BID Date", "QIB", "SHNI", "BHNI",
#         "NII", "RII", "IPO Size", "IPO Price", "Lot", "P/E", "Close Date",
#         "~id", "~URLRewrite_Folder_Name", "~Highlight_Row", "~IPO_Category"
#     ]
#     all_ipo_data["subscription_and_performance"]["live_subscription_report"] = fetch_and_clean_data(
#         "IPO Live Subscription Report",
#         "https://webnodejs.investorgain.com/cloud/report/data-read/333/1/6/2025/2025-26/0/all?search=&v=23-51",
#         subscription_fields
#     )
#     time.sleep(1)

#     gmp_performance_fields = [
#         "~orderby", "IPO", "Listing Date", "IPO_Size", "Subscription", "GMP",
#         "IPO Price", "~id", "Estimated Price", "Listing Price",
#         "Closing Price", "LTP", "~URLRewrite_Folder_Name", "~Last Updated",
#         "~IPO_Category"
#     ]
#     all_ipo_data["subscription_and_performance"]["gmp_performance_tracker"] = fetch_and_clean_data(
#         "IPO GMP Performance Tracker",
#         "https://webnodejs.investorgain.com/cloud/report/data-read/377/1/6/2025/2025-26/0/all?search=&v=22-50",
#         gmp_performance_fields
#     )
#     time.sleep(1)

#     # IPO Calendar / Events API
#     ipo_events_fields = [
#         "Date", "Day", "~Highlight_Row", "Open", "Close", "Unblock (stock names)", "Listing"
#     ]
#     all_ipo_data["ipo_calendar_events"] = fetch_and_clean_data(
#         "Latest & Upcoming IPO Events",
#         "https://webnodejs.investorgain.com/cloud/report/data-read/554/1/6/2025/2025-26/0/0?search=&v=23-50",
#         ipo_events_fields
#     )
#     time.sleep(1)

#     # Save data to JSON file
#     output_filename = "api_scrap_ipo_data.json"
#     with open(output_filename, 'w', encoding='utf-8') as f:
#         json.dump(all_ipo_data, f, indent=4, ensure_ascii=False)
#     print(f"\nAll scraped data saved to {output_filename}")

# if __name__ == "__main__":
#     main()


import requests
import json
import time
from bs4 import BeautifulSoup
import re 
from datetime import datetime

def clean_text_from_html(html_string):
    """Strips HTML tags and cleans up extra whitespace from a string."""
    if not isinstance(html_string, str):
        return html_string
    soup = BeautifulSoup(html_string, 'html.parser')
    clean_text = soup.get_text(separator=' ', strip=True)
    return clean_text

def clean_specific_field(field_name, value):
    """Applies specific cleaning rules based on the field name."""
    if not isinstance(value, str):
        return value

    # First, apply general HTML stripping for all string values
    clean_value = clean_text_from_html(value)

    if field_name in ["GMP", "Est Listing", "IPO Size", "IPO Price", "Price",
                      "Estimated Price", "Listing Price", "Closing Price", "LTP",
                      "Issue Price (Rs.)", "Issue Amount (Rs.cr.)", "Size (Rs Cr)"]:
        # Remove currency symbols, percentage signs, and extra spaces around values
        clean_value = clean_value.replace('₹', '').replace('&#8377;', '').strip()
        clean_value = re.sub(r'\(\s*[\d\.]+\s*%\)', '', clean_value).strip() # Remove (XX.XX%) like (38.02%)
        clean_value = clean_value.replace(',', '') # Remove commas from numbers
    elif field_name in ["Sub", "Total", "QIB", "sNII", "bNII", "NII", "Retail", "Employee", "Others"]:
        clean_value = clean_value.replace('x', '').strip()
    elif field_name in ["Name", "IPO", "Company", "Company Name"]: # Added "Company" and "Company Name" for Chittorgarh
        # Additional cleaning for names:
        # 1. Remove specific markers like <span >U</span> or <span >O</span>
        clean_value = re.sub(r'\s*<span[^>]*>.*?<\/span>', '', clean_value).strip()
        # 2. Remove "IPO", "BSE SME", "NSE SME" suffixes and similar patterns
        clean_value = clean_value.replace(' IPO', '').replace(' BSE SME', '').replace(' NSE SME', '').strip()
        # 3. Remove patterns like "L@XXX.XX (YY.YY%)" from the name
        clean_value = re.sub(r'L@[\d\.]+\s*\([\d\.]+\%\)', '', clean_value).strip()
    
    return clean_value

def parse_date(date_string, source_api_type="investorgain"):
    """
    Parses a date string into a datetime object based on the source API format.
    'chittorgarh_json': ISO format (e.g., "2025-06-30T00:00:00.000Z")
    'chittorgarh_html': "Mon, Jun 30, 2025" or similar (BeautifulSoup will handle initial parsing)
    'investorgain': "DD-Mon-YYYY" (e.g., "30-Jun-2025")
    """
    if not isinstance(date_string, str) or not date_string:
        return None
    
    try:
        if source_api_type == 'chittorgarh_json':
            return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        elif source_api_type == 'investorgain':
            # Adjust to handle dates like "2-Jul" which only have day and month
            if len(date_string.split('-')) == 2: # e.g., "2-Jul"
                current_year = datetime.now().year
                date_string_with_year = f"{date_string}-{current_year}"
                return datetime.strptime(date_string_with_year, '%d-%b-%Y')
            return datetime.strptime(date_string, '%d-%b-%Y')
        elif source_api_type == 'chittorgarh_html':
            # Chittorgarh HTML often has dates like 'Jan 01, 2025' or 'Mon, Jun 30, 2025'
            # We'll try common formats.
            try:
                return datetime.strptime(date_string.replace('th', '').replace('st', '').replace('nd', '').replace('rd', ''), '%b %d, %Y')
            except ValueError:
                try:
                    return datetime.strptime(date_string.replace('th', '').replace('st', '').replace('nd', '').replace('rd', ''), '%a, %b %d, %Y')
                except ValueError:
                    return datetime.strptime(date_string.replace('th', '').replace('st', '').replace('nd', '').replace('rd', ''), '%d %b, %Y')
        else:
            return None
    except ValueError:
        # print(f"Warning: Could not parse date '{date_string}' with format type '{source_api_type}'")
        return None

def generate_canonical_id(ipo_details, source_api_type):
    """
    Generates a consistent canonical ID for an IPO based on available details.
    Prioritizes ID + Date, then Cleaned Name + Date.
    """
    ipo_id = str(ipo_details.get("id", "")) if ipo_details.get("id") is not None else ""
    
    company_name_raw = None
    opening_date_raw = None

    if source_api_type.startswith("chittorgarh"):
        company_name_raw = ipo_details.get("Company") or ipo_details.get("Company Name") or ipo_details.get("IPO")
        opening_date_raw = ipo_details.get("Issue_Open_Date") or ipo_details.get("Opening Date") or ipo_details.get("Open Date")
    else: # Investorgain
        company_name_raw = ipo_details.get("Name") or ipo_details.get("IPO")
        opening_date_raw = ipo_details.get("Open") # Investorgain's opening date field

    cleaned_company_name = clean_specific_field("Name", company_name_raw) # Use "Name" for general cleaning

    opening_date_obj = parse_date(opening_date_raw, source_api_type) # Pass the specific type

    date_part = opening_date_obj.strftime('%Y%m%d') if opening_date_obj else "no_date"

    if ipo_id and ipo_id != "":
        return f"id_{ipo_id}_{date_part}"
    elif cleaned_company_name and cleaned_company_name != "":
        # Further normalize name for key generation (lowercase, replace non-alphanumeric with underscores)
        normalized_name_for_key = re.sub(r'[^a-z0-9]+', '_', cleaned_company_name.lower()).strip('_')
        return f"{normalized_name_for_key}_{date_part}"
    return None # Cannot generate a reliable ID

def fetch_and_process_json_api_data(api_name, url, api_category, expected_fields, source_site):
    """
    Fetches JSON data from a given API, cleans relevant fields, and returns a list of
    dictionaries with an added 'source_api' and 'api_category' field.
    Handles both Investorgain and Chittorgarh JSON APIs.
    """
    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    if source_site == "Investorgain":
        headers["Origin"] = "https://www.investorgain.com"
        headers["Referer"] = "https://www.investorgain.com/"
    elif source_site == "Chittorgarh":
        headers["Origin"] = "https://www.chittorgarh.com"
        headers["Referer"] = "https://www.chittorgarh.com/"

    print(f"Fetching data for: {api_name} ({api_category}) from {url}")
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status() # Raise an exception for bad status codes

        data = response.json()
        report_data = data.get("reportTableData", [])

        processed_records = []
        for record in report_data:
            processed_record = {"source_api": api_name, "api_category": api_category, "source_site": source_site}
            for field in expected_fields:
                original_field_name = field
                # Remove '~' prefix for cleaner keys in the processed record
                cleaned_field_name = field.replace('~', '')

                value = record.get(original_field_name, "")

                # Apply general and specific cleaning
                processed_record[cleaned_field_name] = clean_specific_field(cleaned_field_name, value)
            processed_records.append(processed_record)

        print(f"Successfully fetched {len(processed_records)} records for {api_name}.")
        return processed_records

    except requests.exceptions.RequestException as e:
        print(f"Error fetching {api_name}: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON for {api_name}: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred for {api_name}: {e}")
        return []

def fetch_and_process_html_table(api_name, url, api_category, source_site):
    """
    Fetches data from an HTML table, parses it, cleans fields, and returns a list of dictionaries.
    Specifically for Chittorgarh's SME IPO Performance Tracker.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "https://www.chittorgarh.com/"
    }

    print(f"Fetching HTML data for: {api_name} ({api_category}) from {url}")
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the table containing the performance data
        # Inspecting the page (chittorgarh.com/ipo/ipo_perf_tracker.asp?exchange=sme)
        # shows the main table has class "table table-striped table-bordered"
        table = soup.find('table', class_='table table-striped table-bordered')
        
        if not table:
            print(f"Error: Table not found on page for {api_name}")
            return []

        headers = [clean_text_from_html(th.get_text()) for th in table.find('thead').find_all('th')]
        
        processed_records = []
        for row in table.find('tbody').find_all('tr'):
            cols = row.find_all('td')
            if not cols:
                continue

            record = {"source_api": api_name, "api_category": api_category, "source_site": source_site}
            for i, header_name in enumerate(headers):
                if i < len(cols):
                    field_value = cols[i].get_text(strip=True)
                    # Use a general cleaning for these fields, as HTML tags are stripped by get_text(strip=True)
                    # and specific cleaning for values like numbers etc.
                    record[header_name.replace(' ', '_')] = clean_specific_field(header_name, field_value)
            processed_records.append(record)

        print(f"Successfully fetched {len(processed_records)} records for {api_name}.")
        return processed_records

    except requests.exceptions.RequestException as e:
        print(f"Error fetching {api_name}: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred for {api_name}: {e}")
        return []

def main():
    ipo_data_by_canonical_id = {} # Stores merged IPO data based on canonical ID

    # Define fields for different API types from Investorgain
    investorgain_gmp_fields = [
        "~orderby1", "Name", "GMP", "Fire Rating", "Sub", "Price",
        "Est Listing", "IPO Size", "Lot", "~P/E", "~id", "Open", "Close",
        "BoA Dt", "Listing", "~Srt_Open", "~Srt_Close", "~Srt_BoA_Dt",
        "~Str_Listing", "~urlrewrite_folder_name", "GMP Updated",
        "~Display_Order", "~Highlight_Row", "~IPO_Category"
    ]

    investorgain_subscription_fields = [
        "~idobid", "~end_dt", "Name", "Total", "BID Date", "QIB", "SHNI", "BHNI",
        "NII", "RII", "IPO Size", "IPO Price", "Lot", "P/E", "Close Date",
        "~id", "~URLRewrite_Folder_Name", "~Highlight_Row", "~IPO_Category"
    ]

    investorgain_gmp_performance_fields = [
        "~orderby", "IPO", "Listing Date", "IPO_Size", "Subscription", "GMP",
        "IPO Price", "~id", "Estimated Price", "Listing Price",
        "Closing Price", "LTP", "~URLRewrite_Folder_Name", "~Last Updated",
        "~IPO_Category"
    ]

    investorgain_ipo_events_fields = [
        "Date", "Day", "~Highlight_Row", "Open", "Close", "Unblock (stock names)", "Listing"
    ]

    # Define fields for different API types from Chittorgarh (JSON APIs)
    chittorgarh_basic_ipo_fields = [
        "Company", "Opening Date", "Closing Date", "Listing Date", "Issue Price (Rs.)", "Issue Amount (Rs.cr.)",
        "~IPO", "~URLRewrite_Folder_Name", "~Display_order", "~Issue_Open_Date", "~IssueCloseDate",
        "~ListingDate", "~Highlight_Row", "~compare_name", "~compare_image", "~orderdate", "Listing at", "Lead Manager"
    ]

    chittorgarh_mainboard_subscription_fields = [
        "~id", "Company Name", "~URLRewrite_Folder_Name", "Close Date", "Size (Rs Cr)",
        "QIB (x)", "sNII (x)", "bNII (x)", "NII (x)", "Retail (x)", "Employee (x)", "Others (x)",
        "Total (x)", "Applications", "~Issue_Close_Date", "~Issue_Open_Date", "~Highlight_Row"
    ]

    chittorgarh_sme_subscription_fields = [
        "~id", "Company Name", "~URLRewrite_Folder_Name", "Open Date", "Close Date", "Size (Rs Cr)",
        "QIB (x)", "NII (x)", "Retail (x)", "Total (x)", "Applications",
        "~Issue_Close_Date", "~Issue_Open_Date", "~Highlight_Row"
    ]

    all_api_configs = [
        # Investorgain APIs
        {"name": "IG All IPO GMP", "url": "https://webnodejs.investorgain.com/cloud/report/data-read/331/1/6/2025/2025-26/0/all?search=&v=23-18", "category": "gmp_details", "fields": investorgain_gmp_fields, "source_site": "Investorgain"},
        {"name": "IG Live Mainboard GMP", "url": "https://webnodejs.investorgain.com/cloud/report/data-read/331/1/6/2025/2025-26/0/ipo?search=&v=23-49", "category": "gmp_details", "fields": investorgain_gmp_fields, "source_site": "Investorgain"},
        {"name": "IG Live SME GMP", "url": "https://webnodejs.investorgain.com/cloud/report/data-read/331/1/6/2025/2025-26/0/sme?search=&v=23-18", "category": "gmp_details", "fields": investorgain_gmp_fields, "source_site": "Investorgain"},
        {"name": "IG Current & Upcoming IPO GMP", "url": "https://webnodejs.investorgain.com/cloud/report/data-read/331/1/6/2025/2025-26/0/current?search=&v=23-49", "category": "gmp_details", "fields": investorgain_gmp_fields, "source_site": "Investorgain"},
        {"name": "IG Closed IPO GMP", "url": "https://webnodejs.investorgain.com/cloud/report/data-read/331/1/6/2025/2025-26/0/close?search=&v=23-49", "category": "gmp_details", "fields": investorgain_gmp_fields, "source_site": "Investorgain"},
        {"name": "IG Listed IPO GMP", "url": "https://webnodejs.investorgain.com/cloud/report/data-read/331/1/6/2025/2025-26/0/listed?search=&v=23-49", "category": "gmp_details", "fields": investorgain_gmp_fields, "source_site": "Investorgain"},
        {"name": "IG IPO Live Subscription Report", "url": "https://webnodejs.investorgain.com/cloud/report/data-read/333/1/6/2025/2025-26/0/all?search=&v=23-51", "category": "subscription_and_performance", "fields": investorgain_subscription_fields, "source_site": "Investorgain"},
        {"name": "IG IPO GMP Performance Tracker", "url": "https://webnodejs.investorgain.com/cloud/report/data-read/377/1/6/2025/2025-26/0/all?search=&v=22-50", "category": "subscription_and_performance", "fields": investorgain_gmp_performance_fields, "source_site": "Investorgain"},
        {"name": "IG Latest & Upcoming IPO Events", "url": "https://webnodejs.investorgain.com/cloud/report/data-read/554/1/6/2025/2025-26/0/0?search=&v=23-50", "category": "ipo_calendar_events", "fields": investorgain_ipo_events_fields, "source_site": "Investorgain"},
        
        # Chittorgarh JSON APIs
        {"name": "CG Mainboard Current IPOs", "url": "https://webnodejs.chittorgarh.com/cloud/report/data-read/82/1/6/2025/2025-26/0/mainboard/0?search=&v=22-05", "category": "basic_ipo_details", "fields": chittorgarh_basic_ipo_fields, "source_site": "Chittorgarh"},
        {"name": "CG SME Current IPOs", "url": "https://webnodejs.chittorgarh.com/cloud/report/data-read/82/1/6/2025/2025-26/0/sme/0?search=&v=22-45", "category": "basic_ipo_details", "fields": chittorgarh_basic_ipo_fields, "source_site": "Chittorgarh"},
        {"name": "CG All IPOs", "url": "https://webnodejs.chittorgarh.com/cloud/report/data-read/82/1/6/2025/2025-26/0/all/0?search=&v=22-45", "category": "basic_ipo_details", "fields": chittorgarh_basic_ipo_fields, "source_site": "Chittorgarh"},
        {"name": "CG Mainboard IPO Subscription Status", "url": "https://webnodejs.chittorgarh.com/cloud/report/data-read/21/1/6/2025/2025-26/0/0/0?search=&v=21-22", "category": "subscription_status", "fields": chittorgarh_mainboard_subscription_fields, "source_site": "Chittorgarh"},
        {"name": "CG SME IPO Subscription Status", "url": "https://webnodejs.chittorgarh.com/cloud/report/data-read/22/1/6/2025/2025-26/0/0/0?search=&v=17-56", "category": "subscription_status", "fields": chittorgarh_sme_subscription_fields, "source_site": "Chittorgarh"},
        
        # Chittorgarh HTML Table API
        {"name": "CG SME IPO Performance Tracker", "url": "https://www.chittorgarh.com/ipo/ipo_perf_tracker.asp?exchange=sme&_rsc=w85j8", "category": "listed_performance", "is_html_table": True, "source_site": "Chittorgarh"}
    ]

    for config in all_api_configs:
        records = []
        if config.get("is_html_table"):
            records = fetch_and_process_html_table(
                config["name"], config["url"], config["category"], config["source_site"]
            )
        else:
            records = fetch_and_process_json_api_data(
                config["name"], config["url"], config["category"], config["fields"], config["source_site"]
            )

        for record in records:
            source_site_type = "chittorgarh_json"
            if config.get("is_html_table"):
                source_site_type = "chittorgarh_html"
            elif config["source_site"] == "Investorgain":
                source_site_type = "investorgain"

            canonical_id = generate_canonical_id(record, source_site_type)
            
            if canonical_id:
                if canonical_id not in ipo_data_by_canonical_id:
                    # Initialize with common identifiers
                    initial_record = {
                        "canonical_id": canonical_id,
                        "cleaned_name": clean_specific_field("Name", record.get("Name") or record.get("IPO") or record.get("Company") or record.get("Company Name")),
                        "data_sources": {}
                    }
                    ipo_data_by_canonical_id[canonical_id] = initial_record
                
                # Add data from the current API endpoint to the IPO's entry
                # We'll store it under the API's name to avoid field collisions
                # and to know where the data originated.
                ipo_data_by_canonical_id[canonical_id]["data_sources"][config["name"]] = record
            else:
                # Handle records that cannot be mapped by ID or Name (e.g., generic calendar events
                # or unmappable HTML table entries)
                if config["category"] == "ipo_calendar_events":
                    # For Investorgain IPO Events, they don't have a direct IPO ID, so we store them separately
                    if "investorgain_ipo_calendar_events_details" not in ipo_data_by_canonical_id:
                        ipo_data_by_canonical_id["investorgain_ipo_calendar_events_details"] = {"events": []}
                    ipo_data_by_canonical_id["investorgain_ipo_calendar_events_details"]["events"].append(record)
                elif config["name"] == "CG SME IPO Performance Tracker" and not canonical_id:
                    # For Chittorgarh SME IPO Performance which might not have strong IDs
                    if "cg_sme_performance_unmapped" not in ipo_data_by_canonical_id:
                        ipo_data_by_canonical_id["cg_sme_performance_unmapped"] = {"records": []}
                    ipo_data_by_canonical_id["cg_sme_performance_unmapped"]["records"].append(record)
                else:
                    print(f"Warning: Could not map record to a canonical ID: {record.get('Name') or record.get('IPO') or record.get('Company') or record.get('Company Name')} (API: {config['name']})")
        
        time.sleep(1) # Be polite and avoid hitting rate limits too hard

    # --- START MODIFICATION FOR DESIRED OUTPUT FORMAT ---

    final_transformed_output = {}
    for canonical_id, ipo_details in ipo_data_by_canonical_id.items():
        # Exclude non-IPO specific entries that were stored under special keys
        if canonical_id in ["investorgain_ipo_calendar_events_details", "cg_sme_performance_unmapped"]:
            final_transformed_output[canonical_id] = ipo_details # Keep these as-is for now
            continue

        cleaned_name = ipo_details.get("cleaned_name")
        if cleaned_name:
            # This directly assigns the IPO object to the cleaned_name key.
            # As discussed, if cleaned_name is not strictly unique for non-merged IPOs,
            # this will overwrite earlier entries with the same cleaned_name.
            final_transformed_output[cleaned_name] = ipo_details
        else:
            print(f"Warning: IPO with canonical_id '{canonical_id}' has no cleaned_name. Skipping transformation to top-level key.")
            # Optionally, you might want to include these under a fallback key or log them.
            final_transformed_output[f"unnamed_ipo_{canonical_id}"] = ipo_details # Fallback for un-named IPOs

    # --- END MODIFICATION ---

    # Save data to JSON file
    output_filename = "combined_ipo_data_transformed.json" # New filename for clarity
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(final_transformed_output, f, indent=4, ensure_ascii=False)
    print(f"\nAll scraped and mapped data saved to {output_filename}")

if __name__ == "__main__":
    main()



# import requests
# import json
# import time
# from bs4 import BeautifulSoup
# import re # For more precise regex cleaning if needed
# from datetime import datetime

# def clean_text_from_html(html_string):
#     """Strips HTML tags and cleans up extra whitespace from a string."""
#     if not isinstance(html_string, str):
#         return html_string
#     soup = BeautifulSoup(html_string, 'html.parser')
#     clean_text = soup.get_text(separator=' ', strip=True)
#     return clean_text

# def clean_specific_field(field_name, value):
#     """Applies specific cleaning rules based on the field name."""
#     if not isinstance(value, str):
#         return value

#     # First, apply general HTML stripping for all string values
#     clean_value = clean_text_from_html(value)

#     if field_name in ["GMP", "Est Listing", "IPO Size", "IPO Price", "Price",
#                       "Estimated Price", "Listing Price", "Closing Price", "LTP",
#                       "Issue Price (Rs.)", "Issue Amount (Rs.cr.)", "Size (Rs Cr)"]:
#         # Remove currency symbols, percentage signs, and extra spaces around values
#         clean_value = clean_value.replace('₹', '').replace('&#8377;', '').strip()
#         clean_value = re.sub(r'\(\s*[\d\.]+\s*%\)', '', clean_value).strip() # Remove (XX.XX%) like (38.02%)
#         clean_value = clean_value.replace(',', '') # Remove commas from numbers
#     elif field_name in ["Sub", "Total", "QIB", "sNII", "bNII", "NII", "Retail", "Employee", "Others"]:
#         clean_value = clean_value.replace('x', '').strip()
#     elif field_name in ["Name", "IPO", "Company", "Company Name"]: # Added "Company" and "Company Name" for Chittorgarh
#         # Additional cleaning for names:
#         # 1. Remove specific markers like <span >U</span> or <span >O</span>
#         clean_value = re.sub(r'\s*<span[^>]*>.*?<\/span>', '', clean_value).strip()
#         # 2. Remove "IPO", "BSE SME", "NSE SME" suffixes and similar patterns
#         clean_value = clean_value.replace(' IPO', '').replace(' BSE SME', '').replace(' NSE SME', '').strip()
#         # 3. Remove patterns like "L@XXX.XX (YY.YY%)" from the name
#         clean_value = re.sub(r'L@[\d\.]+\s*\([\d\.]+\%\)', '', clean_value).strip()
    
#     return clean_value

# def parse_date(date_string, source_api_type="investorgain"):
#     """
#     Parses a date string into a datetime object based on the source API format.
#     'chittorgarh_json': ISO format (e.g., "2025-06-30T00:00:00.000Z")
#     'chittorgarh_html': "Mon, Jun 30, 2025" or similar (BeautifulSoup will handle initial parsing)
#     'investorgain': "DD-Mon-YYYY" (e.g., "30-Jun-2025") or "DD-Mon"
#     """
#     if not isinstance(date_string, str) or not date_string:
#         return None
    
#     try:
#         if source_api_type == 'chittorgarh_json':
#             return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
#         elif source_api_type == 'investorgain':
#             # Handle "DD-Mon-YYYY" or "DD-Mon"
#             if len(date_string.split('-')) == 2: # e.g., "26-Jun"
#                 current_year = datetime.now().year
#                 date_string_with_year = f"{date_string}-{current_year}"
#                 return datetime.strptime(date_string_with_year, '%d-%b-%Y')
#             return datetime.strptime(date_string, '%d-%b-%Y')
#         elif source_api_type == 'chittorgarh_html':
#             # Chittorgarh HTML often has dates like 'Jan 01, 2025' or 'Mon, Jun 30, 2025'
#             # We'll try common formats.
#             try:
#                 return datetime.strptime(date_string.replace('th', '').replace('st', '').replace('nd', '').replace('rd', ''), '%b %d, %Y')
#             except ValueError:
#                 try:
#                     return datetime.strptime(date_string.replace('th', '').replace('st', '').replace('nd', '').replace('rd', ''), '%a, %b %d, %Y')
#                 except ValueError:
#                     try: # Added for cases like '30 Jun, 2025'
#                         return datetime.strptime(date_string.replace('th', '').replace('st', '').replace('nd', '').replace('rd', ''), '%d %b, %Y')
#                     except ValueError:
#                         return None # If all formats fail
#         else:
#             return None
#     except ValueError:
#         # print(f"Warning: Could not parse date '{date_string}' with format type '{source_api_type}'")
#         return None

# def generate_canonical_id(ipo_details, source_api_type):
#     """
#     Generates a consistent canonical ID for an IPO based on available details.
#     Prioritizes ID + Date, then Cleaned Name + Date.
#     """
#     ipo_id = str(ipo_details.get("id", "")) if ipo_details.get("id") is not None else ""
    
#     company_name_raw = None
#     opening_date_raw = None

#     if source_api_type.startswith("chittorgarh"):
#         company_name_raw = ipo_details.get("Company") or ipo_details.get("Company Name") or ipo_details.get("IPO")
#         # Prioritize ISO date if available, otherwise human-readable
#         opening_date_raw = ipo_details.get("Issue_Open_Date") or ipo_details.get("Opening Date") or ipo_details.get("Open Date")
#     else: # Investorgain
#         company_name_raw = ipo_details.get("Name") or ipo_details.get("IPO")
#         opening_date_raw = ipo_details.get("Open") # Investorgain's opening date field

#     cleaned_company_name = clean_specific_field("Name", company_name_raw) # Use "Name" for general cleaning

#     opening_date_obj = parse_date(opening_date_raw, source_api_type) # Pass the specific type

#     date_part = opening_date_obj.strftime('%Y%m%d') if opening_date_obj else "no_date"

#     if ipo_id and ipo_id != "":
#         return f"id_{ipo_id}_{date_part}"
#     elif cleaned_company_name and cleaned_company_name != "":
#         # Further normalize name for key generation (lowercase, replace non-alphanumeric with underscores)
#         normalized_name_for_key = re.sub(r'[^a-z0-9]+', '_', cleaned_company_name.lower()).strip('_')
#         return f"{normalized_name_for_key}_{date_part}"
#     return None # Cannot generate a reliable ID

# def fetch_and_process_json_api_data(api_name, url, api_category, expected_fields, source_site):
#     """
#     Fetches JSON data from a given API, cleans relevant fields, and returns a list of
#     dictionaries with an added 'source_api' and 'api_category' field.
#     Handles both Investorgain and Chittorgarh JSON APIs.
#     """
#     headers = {
#         "Accept": "application/json",
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
#     }

#     if source_site == "Investorgain":
#         headers["Origin"] = "https://www.investorgain.com"
#         headers["Referer"] = "https://www.investorgain.com/"
#     elif source_site == "Chittorgarh":
#         headers["Origin"] = "https://www.chittorgarh.com"
#         headers["Referer"] = "https://www.chittorgarh.com/"

#     print(f"Fetching data for: {api_name} ({api_category}) from {url}")
#     try:
#         response = requests.get(url, headers=headers, timeout=15)
#         response.raise_for_status() # Raise an exception for bad status codes

#         data = response.json()
#         report_data = data.get("reportTableData", [])

#         processed_records = []
#         for record in report_data:
#             processed_record = {"source_api": api_name, "api_category": api_category, "source_site": source_site}
#             for field in expected_fields:
#                 original_field_name = field
#                 # Remove '~' prefix for cleaner keys in the processed record
#                 cleaned_field_name = field.replace('~', '')

#                 value = record.get(original_field_name, "")

#                 # Apply general and specific cleaning
#                 processed_record[cleaned_field_name] = clean_specific_field(cleaned_field_name, value)
#             processed_records.append(processed_record)

#         print(f"Successfully fetched {len(processed_records)} records for {api_name}.")
#         return processed_records

#     except requests.exceptions.RequestException as e:
#         print(f"Error fetching {api_name}: {e}")
#         return []
#     except json.JSONDecodeError as e:
#         print(f"Error decoding JSON for {api_name}: {e}")
#         return []
#     except Exception as e:
#         print(f"An unexpected error occurred for {api_name}: {e}")
#         return []

# def fetch_and_process_html_table(api_name, url, api_category, source_site):
#     """
#     Fetches data from an HTML table, parses it, cleans fields, and returns a list of dictionaries.
#     Specifically for Chittorgarh's SME IPO Performance Tracker.
#     """
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
#         "Referer": "https://www.chittorgarh.com/"
#     }

#     print(f"Fetching HTML data for: {api_name} ({api_category}) from {url}")
#     try:
#         response = requests.get(url, headers=headers, timeout=15)
#         response.raise_for_status()
        
#         soup = BeautifulSoup(response.text, 'html.parser')
        
#         # Find the table containing the performance data
#         # Inspecting the page (chittorgarh.com/ipo/ipo_perf_tracker.asp?exchange=sme)
#         # shows the main table has class "table table-striped table-bordered"
#         table = soup.find('table', class_='table table-striped table-bordered')
        
#         if not table:
#             print(f"Error: Table not found on page for {api_name}")
#             return []

#         headers = [clean_text_from_html(th.get_text()) for th in table.find('thead').find_all('th')]
        
#         processed_records = []
#         for row in table.find('tbody').find_all('tr'):
#             cols = row.find_all('td')
#             if not cols:
#                 continue

#             record = {"source_api": api_name, "api_category": api_category, "source_site": source_site}
#             for i, header_name in enumerate(headers):
#                 if i < len(cols):
#                     field_value = cols[i].get_text(strip=True)
#                     # Use a general cleaning for these fields, as HTML tags are stripped by get_text(strip=True)
#                     # and specific cleaning for values like numbers etc.
#                     record[header_name.replace(' ', '_')] = clean_specific_field(header_name, field_value)
#             processed_records.append(record)

#         print(f"Successfully fetched {len(processed_records)} records for {api_name}.")
#         return processed_records

#     except requests.exceptions.RequestException as e:
#         print(f"Error fetching {api_name}: {e}")
#         return []
#     except Exception as e:
#         print(f"An unexpected error occurred for {api_name}: {e}")
#         return []

# def consolidate_ipo_data(ipo_entry):
#     """
#     Consolidates data for a single IPO from multiple sources into a unified structure.
#     Applies a basic prioritization strategy for common fields.
#     """
#     consolidated = {
#         "canonical_id": ipo_entry["canonical_id"],
#         "ipo_name": ipo_entry["cleaned_name"], # Use the already cleaned name
#         "source_apis_used": list(ipo_entry["data_sources"].keys()) # Keep track of contributing sources
#     }

#     # Define a prioritization for date fields: Chittorgarh JSON > Investorgain > Chittorgarh HTML
#     date_fields_priority = {
#         "open_date": [
#             ("CG", "Issue_Open_Date", "chittorgarh_json"), # From Chittorgarh JSON (~Issue_Open_Date)
#             ("CG", "Opening Date", "chittorgarh_html"),    # From Chittorgarh HTML/JSON (non-ISO)
#             ("CG", "Open Date", "chittorgarh_json"),       # From Chittorgarh JSON (Open Date in subscription)
#             ("IG", "Open", "investorgain"),                 # From Investorgain
#         ],
#         "close_date": [
#             ("CG", "IssueCloseDate", "chittorgarh_json"),
#             ("CG", "Closing Date", "chittorgarh_html"),
#             ("CG", "Close Date", "chittorgarh_json"),
#             ("IG", "Close", "investorgain"),
#         ],
#         "listing_date": [
#             ("CG", "ListingDate", "chittorgarh_json"),
#             ("CG", "Listing Date", "chittorgarh_html"), # From Chittorgarh HTML table
#             ("IG", "Listing", "investorgain"),
#             ("IG", "Str_Listing", "investorgain"), # Investorgain also has this sorted string date
#         ],
#         "boa_date": [ # Basis of Allotment Date (primarily Investorgain)
#             ("IG", "BoA Dt", "investorgain"),
#             ("IG", "Srt_BoA_Dt", "investorgain"),
#         ]
#     }

#     # Process Date Fields
#     for consolidated_field, source_field_configs in date_fields_priority.items():
#         parsed_date = None
#         for source_prefix, field_name, api_type in source_field_configs:
#             # Iterate through actual data sources for this IPO entry
#             for api_source_name, api_data in ipo_entry["data_sources"].items():
#                 if source_prefix in api_source_name.replace("Investorgain", "IG").replace("Chittorgarh", "CG"):
#                     raw_date_value = api_data.get(field_name)
#                     if raw_date_value:
#                         parsed_date = parse_date(raw_date_value, api_type)
#                         if parsed_date:
#                             consolidated[consolidated_field] = parsed_date.strftime('%Y-%m-%d')
#                             break # Found a date for this field, move to next consolidated field
#             if parsed_date:
#                 break # Found date from a higher priority source, move to next consolidated field

#     # Numeric/Price/Size Fields (take from any source, first found for now)
#     numeric_fields = {
#         "issue_price_range": [
#             ("CG", "Issue Price (Rs.)"),
#             ("IG", "Price") # Investorgain's "Price" is usually a single value from the range
#         ],
#         "issue_size_cr": [
#             ("CG", "Issue Amount (Rs.cr.)"),
#             ("CG", "Size (Rs Cr)"), # Chittorgarh SME Subs Status
#             ("IG", "IPO Size")
#         ],
#         "lot_size": [
#             ("IG", "Lot")
#         ],
#         "gmp_value": [
#             ("IG", "GMP")
#         ],
#         "estimated_listing_price": [
#             ("IG", "Est Listing"),
#             ("IG", "Estimated Price")
#         ],
#         "listing_price": [ # Final listing price, usually from performance trackers
#             ("IG", "Listing Price"),
#             ("CG SME IPO Performance Tracker", "Listing_Price") # From Chittorgarh HTML table
#         ],
#         "closing_price": [
#             ("IG", "Closing Price"),
#             ("IG", "LTP") # Last Traded Price, often same as closing
#         ],
#         "pe_ratio": [
#             ("IG", "P/E")
#         ]
#     }

#     # Process Numeric/Price/Size Fields
#     for consolidated_field, source_field_configs in numeric_fields.items():
#         for source_prefix, field_name in source_field_configs:
#             for api_source_name, api_data in ipo_entry["data_sources"].items():
#                 if source_prefix in api_source_name.replace("Investorgain", "IG").replace("Chittorgarh", "CG"):
#                     value = api_data.get(field_name)
#                     if value is not None and value not in ["", "--"]: # Handle empty strings or specific placeholders
#                         cleaned_value = clean_specific_field(field_name, str(value))
                        
#                         if consolidated_field == "issue_price_range":
#                             consolidated[consolidated_field] = cleaned_value # Keep as string for range
#                         else:
#                             try:
#                                 # Try to convert to int first, then float for whole numbers
#                                 consolidated[consolidated_field] = int(float(cleaned_value)) if float(cleaned_value).is_integer() else float(cleaned_value)
#                             except ValueError:
#                                 consolidated[consolidated_field] = cleaned_value # Keep as string if not convertible
#                         break # Found a value, move to next consolidated field
#             if consolidated_field in consolidated:
#                 break # Found value from a higher priority source or first found

#     # Subscription data (these are generally distinct, prioritize specific subscription reports)
#     subscription_fields_priority = [
#         ("CG Mainboard IPO Subscription Status", ["QIB (x)", "sNII (x)", "bNII (x)", "NII (x)", "Retail (x)", "Employee (x)", "Others (x)", "Total (x)", "Applications"]),
#         ("CG SME IPO Subscription Status", ["QIB (x)", "NII (x)", "Retail (x)", "Total (x)", "Applications"]),
#         ("IG IPO Live Subscription Report", ["QIB", "SHNI", "BHNI", "NII", "RII", "Total"])
#     ]
    
#     subscription_data = {}
#     for source_api_name_full, fields_to_extract in subscription_fields_priority:
#         if source_api_name_full in ipo_entry["data_sources"]:
#             source_data = ipo_entry["data_sources"][source_api_name_full]
#             for field in fields_to_extract:
#                 clean_field_name = field.replace('(x)', '').strip().lower().replace(' ', '_').replace('shni', 'hnii_small').replace('bhni', 'hnii_big').replace('rii', 'retail_individual')
#                 value = source_data.get(field)
#                 if value is not None and value not in ["", "--"]:
#                     cleaned_value = clean_specific_field(field, str(value))
#                     try:
#                         subscription_data[clean_field_name] = float(cleaned_value)
#                     except ValueError:
#                         subscription_data[clean_field_name] = cleaned_value # Keep as string if conversion fails
#             # If we successfully extracted some subscription data from this source, we prioritize it
#             if subscription_data: # Check if subscription_data actually has entries
#                 consolidated["subscription_status"] = subscription_data
#                 break # Stop after finding data from the highest priority subscription source

#     # Other miscellaneous fields (take from first available, prevent overwrites)
#     for api_source_name, api_data in ipo_entry["data_sources"].items():
#         if "IPO_Category" in api_data and "ipo_type" not in consolidated:
#             consolidated["ipo_type"] = api_data["IPO_Category"]
        
#         # Chittorgarh's "Listing at" provides more specific info (e.g., "NSE SME")
#         if "Listing at" in api_data and "listing_exchange" not in consolidated:
#             consolidated["listing_exchange"] = api_data["Listing at"]
        
#         if "Lead Manager" in api_data and "lead_manager" not in consolidated:
#             consolidated["lead_manager"] = api_data["Lead Manager"]
        
#         # 'Lot' might be picked up by numeric, but ensuring here as well
#         if "Lot" in api_data and "lot_size" not in consolidated: 
#             cleaned_value = clean_specific_field("Lot", api_data["Lot"])
#             try:
#                 consolidated["lot_size"] = int(float(cleaned_value)) if float(cleaned_value).is_integer() else float(cleaned_value)
#             except ValueError:
#                 consolidated["lot_size"] = cleaned_value
        
#         if "Fire Rating" in api_data and "fire_rating" not in consolidated:
#             consolidated["fire_rating"] = api_data["Fire Rating"]
        
#         if "urlrewrite_folder_name" in api_data and "url_slug" not in consolidated:
#             consolidated["url_slug"] = api_data["urlrewrite_folder_name"]
        
#         if "compare_image" in api_data and "company_logo_url" not in consolidated:
#             consolidated["company_logo_url"] = api_data["compare_image"]
        
#         if "GMP Updated" in api_data and "gmp_last_updated" not in consolidated:
#             # Parse 'DD-Mon HH:MM' format if needed for a datetime object
#             gmp_update_str = api_data["GMP Updated"]
#             try:
#                 # Add current year to parse "26-Jun 17:28"
#                 current_year = datetime.now().year
#                 gmp_datetime = datetime.strptime(f"{gmp_update_str}-{current_year}", '%d-%b %H:%M-%Y')
#                 consolidated["gmp_last_updated"] = gmp_datetime.isoformat() # Store as ISO string
#             except ValueError:
#                 consolidated["gmp_last_updated"] = gmp_update_str # Store as is if parse fails
        
#         # Add a general description/about field if available, prioritizing Chittorgarh
#         if "About" in api_data and "description" not in consolidated:
#             consolidated["description"] = api_data["About"]

#     return consolidated

# def main():
#     ipo_data_by_canonical_id = {} # Stores merged IPO data based on canonical ID

#     # Define fields for different API types from Investorgain
#     investorgain_gmp_fields = [
#         "~orderby1", "Name", "GMP", "Fire Rating", "Sub", "Price",
#         "Est Listing", "IPO Size", "Lot", "~P/E", "~id", "Open", "Close",
#         "BoA Dt", "Listing", "~Srt_Open", "~Srt_Close", "~Srt_BoA_Dt",
#         "~Str_Listing", "~urlrewrite_folder_name", "GMP Updated",
#         "~Display_Order", "~Highlight_Row", "~IPO_Category"
#     ]

#     investorgain_subscription_fields = [
#         "~idobid", "~end_dt", "Name", "Total", "BID Date", "QIB", "SHNI", "BHNI",
#         "NII", "RII", "IPO Size", "IPO Price", "Lot", "P/E", "Close Date",
#         "~id", "~URLRewrite_Folder_Name", "~Highlight_Row", "~IPO_Category"
#     ]

#     investorgain_gmp_performance_fields = [
#         "~orderby", "IPO", "Listing Date", "IPO_Size", "Subscription", "GMP",
#         "IPO Price", "~id", "Estimated Price", "Listing Price",
#         "Closing Price", "LTP", "~URLRewrite_Folder_Name", "~Last Updated",
#         "~IPO_Category"
#     ]

#     investorgain_ipo_events_fields = [
#         "Date", "Day", "~Highlight_Row", "Open", "Close", "Unblock (stock names)", "Listing"
#     ]

#     # Define fields for different API types from Chittorgarh (JSON APIs)
#     chittorgarh_basic_ipo_fields = [
#         "Company", "Opening Date", "Closing Date", "Listing Date", "Issue Price (Rs.)", "Issue Amount (Rs.cr.)",
#         "~IPO", "~URLRewrite_Folder_Name", "~Display_order", "~Issue_Open_Date", "~IssueCloseDate",
#         "~ListingDate", "~Highlight_Row", "~compare_name", "~compare_image", "~orderdate", "Listing at", "Lead Manager"
#     ]

#     chittorgarh_mainboard_subscription_fields = [
#         "~id", "Company Name", "~URLRewrite_Folder_Name", "Close Date", "Size (Rs Cr)",
#         "QIB (x)", "sNII (x)", "bNII (x)", "NII (x)", "Retail (x)", "Employee (x)", "Others (x)",
#         "Total (x)", "Applications", "~Issue_Close_Date", "~Issue_Open_Date", "~Highlight_Row"
#     ]

#     chittorgarh_sme_subscription_fields = [
#         "~id", "Company Name", "~URLRewrite_Folder_Name", "Open Date", "Close Date", "Size (Rs Cr)",
#         "QIB (x)", "NII (x)", "Retail (x)", "Total (x)", "Applications",
#         "~Issue_Close_Date", "~Issue_Open_Date", "~Highlight_Row"
#     ]

#     all_api_configs = [
#         # Investorgain APIs
#         {"name": "IG All IPO GMP", "url": "https://webnodejs.investorgain.com/cloud/report/data-read/331/1/6/2025/2025-26/0/all?search=&v=23-18", "category": "gmp_details", "fields": investorgain_gmp_fields, "source_site": "Investorgain"},
#         {"name": "IG Live Mainboard GMP", "url": "https://webnodejs.investorgain.com/cloud/report/data-read/331/1/6/2025/2025-26/0/ipo?search=&v=23-49", "category": "gmp_details", "fields": investorgain_gmp_fields, "source_site": "Investorgain"},
#         {"name": "IG Live SME GMP", "url": "https://webnodejs.investorgain.com/cloud/report/data-read/331/1/6/2025/2025-26/0/sme?search=&v=23-18", "category": "gmp_details", "fields": investorgain_gmp_fields, "source_site": "Investorgain"},
#         {"name": "IG Current & Upcoming IPO GMP", "url": "https://webnodejs.investorgain.com/cloud/report/data-read/331/1/6/2025/2025-26/0/current?search=&v=23-49", "category": "gmp_details", "fields": investorgain_gmp_fields, "source_site": "Investorgain"},
#         {"name": "IG Closed IPO GMP", "url": "https://webnodejs.investorgain.com/cloud/report/data-read/331/1/6/2025/2025-26/0/close?search=&v=23-49", "category": "gmp_details", "fields": investorgain_gmp_fields, "source_site": "Investorgain"},
#         {"name": "IG Listed IPO GMP", "url": "https://webnodejs.investorgain.com/cloud/report/data-read/331/1/6/2025/2025-26/0/listed?search=&v=23-49", "category": "gmp_details", "fields": investorgain_gmp_fields, "source_site": "Investorgain"},
#         {"name": "IG IPO Live Subscription Report", "url": "https://webnodejs.investorgain.com/cloud/report/data-read/333/1/6/2025/2025-26/0/all?search=&v=23-51", "category": "subscription_and_performance", "fields": investorgain_subscription_fields, "source_site": "Investorgain"},
#         {"name": "IG IPO GMP Performance Tracker", "url": "https://webnodejs.investorgain.com/cloud/report/data-read/377/1/6/2025/2025-26/0/all?search=&v=22-50", "category": "subscription_and_performance", "fields": investorgain_gmp_performance_fields, "source_site": "Investorgain"},
#         {"name": "IG Latest & Upcoming IPO Events", "url": "https://webnodejs.investorgain.com/cloud/report/data-read/554/1/6/2025/2025-26/0/0?search=&v=23-50", "category": "ipo_calendar_events", "fields": investorgain_ipo_events_fields, "source_site": "Investorgain"},
        
#         # Chittorgarh JSON APIs
#         {"name": "CG Mainboard Current IPOs", "url": "https://webnodejs.chittorgarh.com/cloud/report/data-read/82/1/6/2025/2025-26/0/mainboard/0?search=&v=22-05", "category": "basic_ipo_details", "fields": chittorgarh_basic_ipo_fields, "source_site": "Chittorgarh"},
#         {"name": "CG SME Current IPOs", "url": "https://webnodejs.chittorgarh.com/cloud/report/data-read/82/1/6/2025/2025-26/0/sme/0?search=&v=22-45", "category": "basic_ipo_details", "fields": chittorgarh_basic_ipo_fields, "source_site": "Chittorgarh"},
#         {"name": "CG All IPOs", "url": "https://webnodejs.chittorgarh.com/cloud/report/data-read/82/1/6/2025/2025-26/0/all/0?search=&v=22-45", "category": "basic_ipo_details", "fields": chittorgarh_basic_ipo_fields, "source_site": "Chittorgarh"},
#         {"name": "CG Mainboard IPO Subscription Status", "url": "https://webnodejs.chittorgarh.com/cloud/report/data-read/21/1/6/2025/2025-26/0/0/0?search=&v=21-22", "category": "subscription_status", "fields": chittorgarh_mainboard_subscription_fields, "source_site": "Chittorgarh"},
#         {"name": "CG SME IPO Subscription Status", "url": "https://webnodejs.chittorgarh.com/cloud/report/data-read/22/1/6/2025/2025-26/0/0/0?search=&v=17-56", "category": "subscription_status", "fields": chittorgarh_sme_subscription_fields, "source_site": "Chittorgarh"},
        
#         # Chittorgarh HTML Table API
#         {"name": "CG SME IPO Performance Tracker", "url": "https://www.chittorgarh.com/ipo/ipo_perf_tracker.asp?exchange=sme&_rsc=w85j8", "category": "listed_performance", "is_html_table": True, "source_site": "Chittorgarh"}
#     ]

#     for config in all_api_configs:
#         records = []
#         if config.get("is_html_table"):
#             records = fetch_and_process_html_table(
#                 config["name"], config["url"], config["category"], config["source_site"]
#             )
#         else:
#             records = fetch_and_process_json_api_data(
#                 config["name"], config["url"], config["category"], config["fields"], config["source_site"]
#             )

#         for record in records:
#             source_site_type = "chittorgarh_json"
#             if config.get("is_html_table"):
#                 source_site_type = "chittorgarh_html"
#             elif config["source_site"] == "Investorgain":
#                 source_site_type = "investorgain"

#             canonical_id = generate_canonical_id(record, source_site_type)
            
#             if canonical_id:
#                 if canonical_id not in ipo_data_by_canonical_id:
#                     # Initialize with common identifiers
#                     initial_record = {
#                         "canonical_id": canonical_id,
#                         # Pass source_api_type to clean_specific_field for name cleaning
#                         "cleaned_name": clean_specific_field("Name", record.get("Name") or record.get("IPO") or record.get("Company") or record.get("Company Name")),
#                         "data_sources": {}
#                     }
#                     ipo_data_by_canonical_id[canonical_id] = initial_record
                
#                 # Add data from the current API endpoint to the IPO's entry
#                 # We'll store it under the API's name to avoid field collisions
#                 # and to know where the data originated.
#                 ipo_data_by_canonical_id[canonical_id]["data_sources"][config["name"]] = record
#             else:
#                 # Handle records that cannot be mapped by ID or Name (e.g., generic calendar events
#                 # or unmappable HTML table entries)
#                 if config["category"] == "ipo_calendar_events":
#                     # For Investorgain IPO Events, they don't have a direct IPO ID, so we store them separately
#                     if "investorgain_ipo_calendar_events_details" not in ipo_data_by_canonical_id:
#                         ipo_data_by_canonical_id["investorgain_ipo_calendar_events_details"] = {"events": []}
#                     ipo_data_by_canonical_id["investorgain_ipo_calendar_events_details"]["events"].append(record)
#                 elif config["name"] == "CG SME IPO Performance Tracker" and not canonical_id:
#                     # For Chittorgarh SME IPO Performance which might not have strong IDs
#                     if "cg_sme_performance_unmapped" not in ipo_data_by_canonical_id:
#                         ipo_data_by_canonical_id["cg_sme_performance_unmapped"] = {"records": []}
#                     ipo_data_by_canonical_id["cg_sme_performance_unmapped"]["records"].append(record)
#                 else:
#                     print(f"Warning: Could not map record to a canonical ID: {record.get('Name') or record.get('IPO') or record.get('Company') or record.get('Company Name')} (API: {config['name']})")
        
#         time.sleep(1) # Be polite and avoid hitting rate limits too hard

#     # Transform the canonical_id mapped data into the final consolidated format
#     final_consolidated_ipo_data = {}
#     for canonical_id, ipo_details in ipo_data_by_canonical_id.items():
#         # Exclude non-IPO specific entries that were stored under special keys
#         if canonical_id in ["investorgain_ipo_calendar_events_details", "cg_sme_performance_unmapped"]:
#             # These are not individual IPOs, keep them as is for now or process separately
#             final_consolidated_ipo_data[canonical_id] = ipo_details
#             continue

#         consolidated_record = consolidate_ipo_data(ipo_details)
#         if consolidated_record.get("ipo_name"):
#             final_consolidated_ipo_data[consolidated_record["ipo_name"]] = consolidated_record
#         else:
#             print(f"Warning: Consolidated record for {canonical_id} has no IPO name. Skipping.")


#     # Save consolidated data to JSON file
#     output_filename = "consolidated_ipo_data_for_db.json"
#     with open(output_filename, 'w', encoding='utf-8') as f:
#         json.dump(final_consolidated_ipo_data, f, indent=4, ensure_ascii=False)
#     print(f"\nAll scraped and consolidated data saved to {output_filename}")

# if __name__ == "__main__":
#     main()

