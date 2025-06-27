# # investorgain_scraper.py

# import requests
# import pandas as pd
# from bs4 import BeautifulSoup

# def get_investorgain_data():
#     url = "https://webnodejs.investorgain.com/cloud/report/data-read/331/1/6/2025/2025-26/0/ipo?search=&v=16-18"
#     headers = {
#         "accept": "application/json",
#         "origin": "https://www.investorgain.com",
#         "referer": "https://www.investorgain.com/",
#         "user-agent": "Mozilla/5.0"
#     }

#     print("🔄 Fetching data from InvestorGain...")
#     res = requests.get(url, headers=headers)
#     data = res.json()

#     rows = data.get("reportTableData", [])
#     print(f"✅ Fetched {len(rows)} GMP records from InvestorGain")

#     all_data = []
#     for row in rows:
#         soup = BeautifulSoup(row.get("Name", ""), "html.parser")
#         all_data.append({
#             "IPO Name": soup.text.strip(),
#             "GMP": BeautifulSoup(row.get("GMP", ""), "html.parser").text.strip(),
#             "Est. Listing": BeautifulSoup(row.get("Est Listing", ""), "html.parser").text.strip(),
#             "Fire Rating": BeautifulSoup(row.get("Fire Rating", ""), "html.parser").text.strip(),
#             "P/E": row.get("~P/E", ""),
#             "GMP Updated": row.get("GMP Updated", "")
#         })

#     return pd.DataFrame(all_data)






# import requests
# import json
# import pandas as pd
# import re

# def scrape_ipo_data(base_url, year, financial_year):
#     """
#     Scrapes IPO data from the given API endpoint.
#     """
#     all_ipo_data = []
    
#     params = {
#         'search': '',
#         'v': '16-18',
#         'fldpage_size': 9999,
#     }

#     path_segments = [
#         '331',
#         '1',
#         '6',
#         str(year),
#         financial_year,
#         '0',
#         'ipo'
#     ]
    
#     full_url = f"{base_url}/{'/'.join(path_segments)}"

#     print(f"Attempting to fetch data from: {full_url}")

#     try:
#         response = requests.get(full_url, params=params)
#         response.raise_for_status()

#         data = response.json()

#         if data.get("msg") == 1 and "reportTableData" in data:
#             all_ipo_data.extend(data["reportTableData"])
#             print(f"Successfully retrieved {len(data['reportTableData'])} records.")
            
#             total_records = data.get("totalRecords")
#             current_page_size = data.get("fldpage_size")
            
#             if total_records and current_page_size and total_records > current_page_size:
#                 print(f"Warning: Not all records retrieved in one request. Total records: {total_records}, retrieved: {len(all_ipo_data)}. "
#                       "The API might have a maximum page size limit. You may need to implement pagination logic.")
#             else:
#                 print(f"All {len(all_ipo_data)} records retrieved in a single request.")

#         else:
#             print(f"API response indicates an issue or no data: {data.get('msg')}")
#             print(f"Full response: {data}")

#     except requests.exceptions.HTTPError as http_err:
#         print(f"HTTP error occurred: {http_err}")
#     except requests.exceptions.ConnectionError as conn_err:
#         print(f"Connection error occurred: {conn_err}")
#     except requests.exceptions.Timeout as timeout_err:
#         print(f"Timeout error occurred: {timeout_err}")
#     except requests.exceptions.RequestException as req_err:
#         print(f"An error occurred: {req_err}")
#     except json.JSONDecodeError as json_err:
#         print(f"Failed to decode JSON response: {json_err}")
#         print(f"Response content: {response.text}")

#     return all_ipo_data

# def clean_ipo_data(data):
#     """
#     Cleans and processes the raw IPO data.
#     Converts 'Fire Rating' from emojis to a 0-5 numerical scale
#     and removes the original HTML 'Fire Rating' column.
#     """
#     cleaned_data = []
#     fire_emoji_char = '&#128293;' # The HTML entity for the fire emoji

#     for ipo in data:
#         cleaned_ipo = {}
#         original_fire_rating_html = "" # Store original HTML for processing
        
#         for key, value in ipo.items():
#             if key == "Fire Rating":
#                 original_fire_rating_html = value # Capture the original HTML string
#                 # We will process this outside the loop and add a numerical field
#                 continue # Skip adding the original HTML string directly to cleaned_ipo here
            
#             if isinstance(value, str):
#                 # Generic cleaning for other string fields
#                 value = re.sub(r'<[^>]+>', '', value) # Remove HTML tags
#                 value = value.replace('&#8377;', '₹').replace('&nbsp;', ' ').strip() # Replace HTML entities
#                 value = re.sub(r'\s*\([UC]\)', '', value).strip() # Remove (U) or (C) badges
                
#             cleaned_key = key.replace('~', '')
#             cleaned_ipo[cleaned_key] = value
        
#         # --- Process Fire Rating after general cleaning ---
#         if original_fire_rating_html:
#             fire_count = original_fire_rating_html.count(fire_emoji_char)
#             cleaned_ipo['Fire_Rating_Numerical'] = fire_count
#         else:
#             cleaned_ipo['Fire_Rating_Numerical'] = None # Or 0, depending on desired default

#         # Further specific cleaning for 'Name' to remove badge text
#         if 'Name' in cleaned_ipo:
#             cleaned_ipo['Name'] = re.sub(r'\s*(U|C|L@[\d.]+ \(.*?%\))', '', cleaned_ipo['Name']).strip()
            
#         # Convert numeric strings to actual numbers where appropriate
#         try:
#             cleaned_ipo['Price'] = float(cleaned_ipo['Price'])
#         except (ValueError, KeyError):
#             pass

#         try:
#             gmp_match = re.search(r'\((\d+\.?\d*)%\)', ipo.get('GMP', ''))
#             cleaned_ipo['GMP_Percentage'] = float(gmp_match.group(1)) if gmp_match else None
#         except (AttributeError, KeyError):
#             cleaned_ipo['GMP_Percentage'] = None

#         try:
#             est_listing_match = re.search(r'\((\d+\.?\d*)%\)', ipo.get('Est Listing', ''))
#             cleaned_ipo['Est_Listing_Percentage'] = float(est_listing_match.group(1)) if est_listing_match else None
#         except (AttributeError, KeyError):
#             cleaned_ipo['Est_Listing_Percentage'] = None
            
#         cleaned_data.append(cleaned_ipo)
#     return cleaned_data

# if __name__ == "__main__":
#     api_base_url = "https://webnodejs.investorgain.com/cloud/report/data-read"
#     target_year = 2025
#     target_financial_year = "2025-26"

#     ipo_raw_data = scrape_ipo_data(api_base_url, target_year, target_financial_year)

#     if ipo_raw_data:
#         print(f"\nTotal raw IPO records scraped: {len(ipo_raw_data)}")
        
#         # Clean the data
#         ipo_cleaned_data = clean_ipo_data(ipo_raw_data)
        
#         # --- Output to JSON file ---
#         json_filename = "ipo_data.json"
#         with open(json_filename, 'w', encoding='utf-8') as f:
#             json.dump(ipo_cleaned_data, f, indent=4, ensure_ascii=False)
#         print(f"\nData saved to {json_filename} (JSON format)")

#         # --- Output to Excel file ---
#         excel_filename = "ipo_data.xlsx"
#         try:
#             df = pd.DataFrame(ipo_cleaned_data)
#             # Reorder columns for better readability.
#             # Notice 'Fire Rating' (the original HTML column) is removed from here.
#             desired_columns = [
#                 'Name', 'GMP', 'GMP_Percentage', 'Fire_Rating_Numerical', 
#                 'Price', 'Est Listing', 'Est_Listing_Percentage', 
#                 'IPO Size', 'Lot', 'P/E', 'Open', 'Close', 'BoA Dt', 'Listing', 
#                 'Sub', 'GMP Updated', 'id', 'IPO_Category'
#             ]
#             existing_columns = [col for col in desired_columns if col in df.columns]
#             df = df[existing_columns]
            
#             df.to_excel(excel_filename, index=False, engine='openpyxl')
#             print(f"Data saved to {excel_filename} (Excel format)")
#         except Exception as e:
#             print(f"Error saving to Excel: {e}")
#             print("Please ensure you have 'openpyxl' installed: pip install openpyxl")

#     else:
#         print("No IPO data was retrieved to save.")




import requests
import json
import pandas as pd
import re
import math # For math.ceil to calculate total pages

def scrape_ipo_data_paginated(base_url, year, financial_year):
    """
    Scrapes IPO data from the given API endpoint, handling pagination.

    Args:
        base_url (str): The base URL of the API.
        year (int): The starting year for the data.
        financial_year (str): The financial year string (e.g., "2025-26").

    Returns:
        list: A list of dictionaries, where each dictionary represents an IPO record.
              Returns an empty list if there's an error or no data.
    """
    all_ipo_data = []
    
    # Initial parameters for the first request
    # Set fldpage_size to a reasonable value, perhaps 40 as observed in your response,
    # or a slightly higher number if you've tested it.
    # We will rely on iPageNo for pagination.
    initial_params = {
        'search': '',
        'v': '16-18',
        'fldpage_size': 80, # Start with a known or assumed page size
        'iPageNo': 1       # Start from the first page
    }

    path_segments = [
        '331',
        '1',
        '6',
        str(year),
        financial_year,
        '0',
        'ipo'
    ]
    
    full_url = f"{base_url}/{'/'.join(path_segments)}"
    
    current_page = 1
    total_pages = 1 # Initialize to 1, will be updated after first request
    total_records_expected = 0

    while current_page <= total_pages:
        print(f"Fetching page {current_page} of {total_pages}...")
        
        params = initial_params.copy() # Create a copy to modify page number
        params['iPageNo'] = current_page

        try:
            response = requests.get(full_url, params=params)
            response.raise_for_status() # Raise an HTTPError for bad responses

            data = response.json()

            if data.get("msg") == 1 and "reportTableData" in data:
                all_ipo_data.extend(data["reportTableData"])
                
                # Update total_pages and total_records_expected from the first response
                if current_page == 1:
                    total_records_expected = data.get("totalRecords", 0)
                    reported_page_size = int(data.get("fldpage_size", 1)) # Get the actual page size the API is using
                    
                    if reported_page_size > 0:
                        total_pages = math.ceil(total_records_expected / reported_page_size)
                    else:
                        total_pages = 1 # Avoid division by zero if page size is reported as 0
                    
                    print(f"Total records expected: {total_records_expected}")
                    print(f"Actual page size observed: {reported_page_size}")
                    print(f"Calculated total pages: {total_pages}")
                
            else:
                print(f"API response indicates an issue or no data for page {current_page}: {data.get('msg')}")
                print(f"Full response for page {current_page}: {data}")
                break # Exit loop if an error occurs or no more data

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred on page {current_page}: {http_err}")
            break
        except requests.exceptions.ConnectionError as conn_err:
            print(f"Connection error occurred on page {current_page}: {conn_err}")
            break
        except requests.exceptions.Timeout as timeout_err:
            print(f"Timeout error occurred on page {current_page}: {timeout_err}")
            break
        except requests.exceptions.RequestException as req_err:
            print(f"An error occurred on page {current_page}: {req_err}")
            break
        except json.JSONDecodeError as json_err:
            print(f"Failed to decode JSON response on page {current_page}: {json_err}")
            print(f"Response content: {response.text}")
            break
        
        current_page += 1 # Move to the next page
        
    print(f"Finished scraping. Total records retrieved across all pages: {len(all_ipo_data)}")
    return all_ipo_data


def clean_ipo_data(data):
    """
    Cleans and processes the raw IPO data.
    Converts 'Fire Rating' from emojis to a 0-5 numerical scale
    and removes the original HTML 'Fire Rating' column.
    """
    cleaned_data = []
    fire_emoji_char = '&#128293;' # The HTML entity for the fire emoji

    for ipo in data:
        cleaned_ipo = {}
        original_fire_rating_html = "" 
        
        for key, value in ipo.items():
            if key == "Fire Rating":
                original_fire_rating_html = value
                continue 
            
            if isinstance(value, str):
                value = re.sub(r'<[^>]+>', '', value)
                value = value.replace('&#8377;', '₹').replace('&nbsp;', ' ').strip()
                value = re.sub(r'\s*(U|C|L@[\d.]+ \(.*?%\))', '', value).strip()
                
            cleaned_key = key.replace('~', '')
            cleaned_ipo[cleaned_key] = value
        
        # --- Process Fire Rating after general cleaning ---
        if original_fire_rating_html:
            fire_count = original_fire_rating_html.count(fire_emoji_char)
            cleaned_ipo['Fire_Rating_Numerical'] = fire_count
        else:
            cleaned_ipo['Fire_Rating_Numerical'] = None

        # Further specific cleaning for 'Name' to remove badge text
        if 'Name' in cleaned_ipo:
            cleaned_ipo['Name'] = re.sub(r'\s*(U|C|L@[\d.]+ \(.*?%\))', '', cleaned_ipo['Name']).strip()
            
        # Convert numeric strings to actual numbers where appropriate
        try:
            cleaned_ipo['Price'] = float(cleaned_ipo['Price'])
        except (ValueError, KeyError):
            pass

        try:
            gmp_match = re.search(r'\((\d+\.?\d*)%\)', ipo.get('GMP', ''))
            cleaned_ipo['GMP_Percentage'] = float(gmp_match.group(1)) if gmp_match else None
        except (AttributeError, KeyError):
            cleaned_ipo['GMP_Percentage'] = None

        try:
            est_listing_match = re.search(r'\((\d+\.?\d*)%\)', ipo.get('Est Listing', ''))
            cleaned_ipo['Est_Listing_Percentage'] = float(est_listing_match.group(1)) if est_listing_match else None
        except (AttributeError, KeyError):
            cleaned_ipo['Est_Listing_Percentage'] = None
            
        cleaned_data.append(cleaned_ipo)
    return cleaned_data

if __name__ == "__main__":
    api_base_url = "https://webnodejs.investorgain.com/cloud/report/data-read"
    target_year = 2025
    target_financial_year = "2025-26"

    ipo_raw_data = scrape_ipo_data_paginated(api_base_url, target_year, target_financial_year)

    if ipo_raw_data:
        print(f"\nTotal raw IPO records scraped across all pages: {len(ipo_raw_data)}")
        
        # Clean the data
        ipo_cleaned_data = clean_ipo_data(ipo_raw_data)
        
        # --- Output to JSON file ---
        json_filename = "ipo_data_onvestogain.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(ipo_cleaned_data, f, indent=4, ensure_ascii=False)
        print(f"\nData saved to {json_filename} (JSON format)")

        # --- Output to Excel file ---
        excel_filename = "ipo_data.xlsx"
        try:
            df = pd.DataFrame(ipo_cleaned_data)
            desired_columns = [
                'Name', 'GMP', 'GMP_Percentage', 'Fire_Rating_Numerical', 
                'Price', 'Est Listing', 'Est_Listing_Percentage', 
                'IPO Size', 'Lot', 'P/E', 'Open', 'Close', 'BoA Dt', 'Listing', 
                'Sub', 'GMP Updated', 'id', 'IPO_Category'
            ]
            existing_columns = [col for col in desired_columns if col in df.columns]
            df = df[existing_columns]
            
            df.to_excel(excel_filename, index=False, engine='openpyxl')
            print(f"Data saved to {excel_filename} (Excel format)")
        except Exception as e:
            print(f"Error saving to Excel: {e}")
            print("Please ensure you have 'openpyxl' installed: pip install openpyxl")

    else:
        print("No IPO data was retrieved to save.")

