import requests
from bs4 import BeautifulSoup
import json
import time
import re
from datetime import datetime

def fetch_ipo_list_from_api():
    """
    Fetches the list of IPOs from the Investorgain API.
    """
    api_url = "https://webnodejs.investorgain.com/cloud/ipo/list-read"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get("msg") == 1 and "ipoList" in data:
            return data["ipoList"]
        else:
            print(f"API response not as expected: {data}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Error fetching IPO list from API: {e}")
        return []

def clean_text(text):
    """
    Cleans extracted text by removing extra spaces, newlines, and non-breaking spaces.
    """
    if text:
        text = text.replace('\xa0', ' ').replace('\n', ' ').strip()
        text = re.sub(r'\s+', ' ', text)
    return text

def extract_ipo_important_dates(soup):
    """
    Extracts IPO Important Dates from the IPO detail page by directly targeting
    <strong> tags with core date labels (like "Opening Date") and then getting their next sibling <td>.
    This version processes the strong tag's full text content for matching.
    """
    dates_data = {}
    
    # Define patterns for the core date labels.
    # We now look for just "Opening Date", "Closing Date", "Listing Date" etc.
    # assuming they are unique in the page in this context.
    # The patterns are now simpler as we'll apply them to the cleaned text.
    date_field_patterns = {
        "IPO Open Date": re.compile(r'Opening Date', re.IGNORECASE),
        "IPO Close Date": re.compile(r'Closing Date', re.IGNORECASE),
        "Basis of Allotment": re.compile(r'Basis of Allotment Date', re.IGNORECASE),
        "Initiation of Refunds": re.compile(r'Refunds Initiation', re.IGNORECASE),
        "Credit of Shares to Demat": re.compile(r'Credit of Shares to Demat', re.IGNORECASE),
        "Listing Date": re.compile(r'Listing Date', re.IGNORECASE), 
    }

    # Iterate through all <strong> tags first, then check their text
    all_strong_tags = soup.find_all('strong') # Find all strong tags once

    for output_key, pattern in date_field_patterns.items():
        found = False
        for strong_tag in all_strong_tags:
            strong_text = clean_text(strong_tag.get_text()) # Get and clean the full text content of the strong tag
            
            if pattern.search(strong_text): # Use .search() with the compiled regex on the cleaned text
                # We found the strong tag containing our pattern
                # Now, find its parent <td>
                target_td = strong_tag.find_parent('td')
                if target_td:
                    # The date value is usually in the immediate next sibling <td>
                    value_td = target_td.find_next_sibling('td')
                    if value_td:
                        value = clean_text(value_td.get_text(strip=True))
                        dates_data[output_key] = value
                        found = True
                        break # Break from inner loop once found for this key
        
        # Optional: Add print statements for debugging missing elements
        # if not found:
        #     print(f"  DEBUG: Pattern '{pattern.pattern}' for '{output_key}' not found in any <strong> tag.")


    # Ensure all expected keys are present, even if with 'N/A'
    for key in date_field_patterns.keys():
        if key not in dates_data:
            dates_data[key] = 'N/A'
    
    return dates_data

# Rest of your script (parse_date_status, scrape_ipo_important_dates, save_to_json, print_summary, if __name__ == "__main__":)
# remains exactly the same as in the last version.
# The only changes are within extract_ipo_important_dates.

# ... (rest of the code is unchanged from the previous version) ...

def parse_date_status(date_string):
    """
    Attempts to parse date and determine if it's past, present, or future.
    Handles ordinal suffixes (st, nd, rd, th) in dates.
    Returns tuple: (parsed_date, status, original_string)
    """
    if not date_string or date_string == 'N/A':
        return None, 'Unknown', date_string
    
    # --- NEW: Remove ordinal suffixes (st, nd, rd, th) before parsing ---
    # This regex looks for 1 or 2 digits followed by 'st', 'nd', 'rd', or 'th'
    # and replaces the suffix with an empty string.
    cleaned_date_string = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_string, flags=re.IGNORECASE)
    # -------------------------------------------------------------------

    # Common date patterns to try after cleaning
    # Note: %b is for abbreviated month name (e.g., Jul), %B is for full month name (e.g., July)
    date_formats_to_try = [
        '%d %b %Y',     # e.g., "3 Jul 2025"
        '%d %B %Y',     # e.g., "3 July 2025"
        '%d/%m/%Y',     # e.g., "03/07/2025"
        '%d-%m-%Y',     # e.g., "03-07-2025"
        '%B %d, %Y',    # e.g., "July 3, 2025"
        '%b %d, %Y',    # e.g., "Jul 3, 2025"
        # Add more formats here if you encounter them on the website
    ]
    
    current_date = datetime.now()
    
    for fmt in date_formats_to_try:
        try:
            parsed_date = datetime.strptime(cleaned_date_string, fmt)
            if parsed_date.date() < current_date.date():
                status = 'Past'
            elif parsed_date.date() == current_date.date():
                status = 'Today'
            else:
                status = 'Future'
            return parsed_date, status, date_string # Return original date_string as well
        except ValueError:
            continue # Try the next format

    # If no date pattern matched after cleaning, check for keywords
    if any(word in date_string.lower() for word in ['tba', 'tbd', 'to be announced', 'to be decided']):
        return None, 'TBA', date_string
    elif 'n/a' in date_string.lower():
        return None, 'N/A', date_string
    else:
        return None, 'Unknown', date_string # Still 'Unknown' if no parsing or keyword match



def scrape_ipo_important_dates(base_url="https://www.investorgain.com"):
    """
    Main function to scrape only IPO Important Dates from IPOs.
    """
    all_dates_data = []

    print("Fetching IPO list from API...")
    ipo_list = fetch_ipo_list_from_api()
    if not ipo_list:
        print("No IPOs found or error fetching IPO list. Exiting.")
        return []

    print(f"Found {len(ipo_list)} IPOs via API. Starting IPO Important Dates scraping...")

    for i, ipo_entry in enumerate(ipo_list, 1):
        company_short_name = ipo_entry.get('company_short_name')
        url_rewrite_folder_name = ipo_entry.get('urlrewrite_folder_name')
        ipo_category = ipo_entry.get('ipo_category')
        ipo_id = ipo_entry.get('id')

        if not url_rewrite_folder_name or not ipo_id:
            print(f"[{i}/{len(ipo_list)}] Skipping {company_short_name} - missing URL data")
            continue

        detail_url = f"{base_url}/ipo/{url_rewrite_folder_name}/{ipo_id}/"

        print(f"[{i}/{len(ipo_list)}] Scraping dates for: {company_short_name}")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        try:
            response = requests.get(detail_url, headers=headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            important_dates = extract_ipo_important_dates(soup)
            
            ipo_dates_info = {
                'IPO ID': ipo_id,
                'Company Name': company_short_name,
                'IPO Category': ipo_category,
                'Detail URL': detail_url,
                'Scraping Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            ipo_dates_info.update(important_dates)
            
            key_dates = ['IPO Open Date', 'IPO Close Date', 'Listing Date']
            for key in key_dates:
                if key in important_dates:
                    parsed_date, status, original = parse_date_status(important_dates[key])
                    ipo_dates_info[f'{key} Status'] = status
                    if parsed_date:
                        ipo_dates_info[f'{key} Parsed'] = parsed_date.strftime('%Y-%m-%d')
                    else:
                        ipo_dates_info[f'{key} Parsed'] = 'N/A'
            
            all_dates_data.append(ipo_dates_info)
            
            relevant_keys_found = 0
            for key in ['IPO Open Date', 'IPO Close Date', 'Basis of Allotment', 'Initiation of Refunds', 'Credit of Shares to Demat', 'Listing Date']:
                if ipo_dates_info.get(key) not in ['N/A', None]:
                    relevant_keys_found += 1
            
            print(f"    ✓ Success - Found {relevant_keys_found} relevant date entries.")
            
        except requests.exceptions.RequestException as e:
            print(f"    ✗ Network error for {detail_url}: {e}")
        except Exception as e:
            print(f"    ✗ Parsing error for {detail_url}: {e}")

        time.sleep(1.5)

    return all_dates_data

def save_to_json(data, filename="ipo_important_dates.json"):
    """
    Saves IPO dates data to JSON file.
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"✓ Data saved to JSON: {filename}")
    except IOError as e:
        print(f"✗ Error saving JSON: {e}")

def print_summary(data):
    """
    Prints a summary of the scraped dates data.
    """
    if not data:
        print("No data to summarize.")
        return
    
    total_ipos = len(data)
    ipos_with_dates = 0
    upcoming_ipos = 0
    ongoing_ipos = 0
    completed_ipos = 0
    
    for ipo in data:
        has_dates = any(ipo.get(key, 'N/A') != 'N/A' for key in ['IPO Open Date', 'IPO Close Date', 'Listing Date'])
        if has_dates:
            ipos_with_dates += 1
        
        open_status = ipo.get('IPO Open Date Status', 'Unknown')
        close_status = ipo.get('IPO Close Date Status', 'Unknown')
        
        if open_status == 'Future':
            upcoming_ipos += 1
        elif open_status in ['Today', 'Past'] and close_status in ['Future', 'Today']:
            ongoing_ipos += 1
        elif close_status == 'Past':
            completed_ipos += 1
    
    print(f"\n=== IPO DATES SUMMARY ===")
    print(f"Total IPOs Scraped: {total_ipos}")
    print(f"IPOs with any key date information: {ipos_with_dates}")
    print(f"Upcoming IPOs (Open Date in Future): {upcoming_ipos}")
    print(f"Ongoing IPOs (Open Today/Past, Close Today/Future): {ongoing_ipos}")
    print(f"Completed IPOs (Close Date in Past): {completed_ipos}")
    
    if total_ipos > 0:
        print(f"Data Success Rate (IPOs with key dates): {(ipos_with_dates/total_ipos)*100:.1f}%")
    else:
        print("Data Success Rate: N/A (No IPOs scraped)")

if __name__ == "__main__":
    print("=== IPO Important Dates Scraper (Date Parsing Fix) ===")
    print("This script extracts all important dates from IPO pages including:")
    print("- IPO Open Date")
    print("- IPO Close Date") 
    print("- Basis of Allotment")
    print("- Initiation of Refunds")
    print("- Credit of Shares to Demat")
    print("- Listing Date")
    print("- Date status analysis (Past/Present/Future)")
    
    print("\nStarting scraping process...")
    dates_data = scrape_ipo_important_dates()
    
    if dates_data:
        save_to_json(dates_data)
        print_summary(dates_data)
        
        print(f"\n=== SAMPLE DATA (First IPO) ===")
        if len(dates_data) > 0:
            sample = dates_data[0]
            for key, value in sample.items():
                print(f"{key}: {value}")
                
        upcoming = [ipo for ipo in dates_data if ipo.get('IPO Open Date Status') == 'Future']
        if upcoming:
            print(f"\n=== FIRST 5 UPCOMING IPOs ===")
            for ipo in upcoming[:5]:
                print(f"- {ipo['Company Name']} (Category: {ipo.get('IPO Category', 'N/A')}): Opens on {ipo.get('IPO Open Date', 'N/A')}")
        else:
            print("\nNo upcoming IPOs found in the scraped data.")
    else:
        print("No data was scraped.")
    
    print("\n=== Scraping Complete ===")

    
