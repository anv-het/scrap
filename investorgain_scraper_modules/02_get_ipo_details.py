import requests
from bs4 import BeautifulSoup
import json
import time
import re
from datetime import datetime

def fetch_ipo_list_from_api():
    """
    Fetches the list of IPOs from the Investorgain API.
    This function is reused for the initial list.
    """
    api_url = "https://webnodejs.investorgain.com/cloud/ipo/list-read"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
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
    Handles HTML entities automatically if BeautifulSoup has already parsed them.
    """
    if text:
        text = text.replace('\xa0', ' ').replace('\n', ' ').strip()
        text = re.sub(r'\s+', ' ', text)
    return text

def extract_company_about(soup):
    """
    Extracts the full company name and the 'About Company' paragraph(s) from the soup object.
    Now correctly handles cases where paragraphs are nested within a div immediately after the h3.
    """
    company_full_name = "N/A"
    about_company_text = "N/A"

    print("DEBUG: Starting extract_company_about function")

    # Find the <h3> tag with itemprop="about"
    about_h3 = soup.find('h3', itemprop="about")
    print(f"DEBUG: Found <h3> tag with itemprop='about': {about_h3}")

    if about_h3:
        h3_text = clean_text(about_h3.get_text())
        print(f"DEBUG: Cleaned text from <h3> tag: {h3_text}")

        # Extract "Company Full Name" from the h3 tag's text
        match = re.search(r'About Company\s*-\s*(.+)', h3_text, re.IGNORECASE)
        if match:
            company_full_name = clean_text(match.group(1))
            print(f"DEBUG: Extracted company full name: {company_full_name}")
        else:
            print(f"DEBUG: Could not parse full company name from H3: {h3_text}")

        # MODIFIED LOGIC FOR PARAGRAPHS: Find the <div> immediately after the <h3>
        about_content_container = None
        current_sibling = about_h3.next_sibling
        while current_sibling:
            if isinstance(current_sibling, str): # Skip NavigableString (whitespace, newlines)
                current_sibling = current_sibling.next_sibling
                continue

            if current_sibling.name == 'div':
                about_content_container = current_sibling
                print("DEBUG: Found direct sibling <div> container for about text.")
                break # Found the container, exit loop
            else: # If it's not a div and not just whitespace, it's not the expected container.
                print(f"DEBUG: Next sibling is '{current_sibling.name}', not the expected <div> container. Stopping search for container.")
                break # Stop if we encounter an unexpected tag
            
            current_sibling = current_sibling.next_sibling


        if about_content_container:
            # Now, find all <p> tags *within* this specific div
            about_paragraphs = []
            paragraphs_in_div = about_content_container.find_all('p')
            
            print(f"DEBUG: Found {len(paragraphs_in_div)} <p> tags within the container div.")

            for p_tag in paragraphs_in_div:
                paragraph_text = clean_text(p_tag.get_text())
                if paragraph_text: # Only add if not empty after cleaning
                    about_paragraphs.append(paragraph_text)
                    print(f"DEBUG: Added paragraph: {paragraph_text[:50]}...") # Print snippet for long text
            
            if about_paragraphs:
                about_company_text = "\n\n".join(about_paragraphs) # Join paragraphs with double newline
                print(f"DEBUG: About Company Text (final): {about_company_text[:100]}...") # Print snippet
            else:
                print("DEBUG: No about company paragraphs found within the container div.")
        else:
            print("DEBUG: No 'About Company' content <div> container found after <h3> tag.")
    else:
        print("DEBUG: No <h3> tag with itemprop='about' found.")


    return {
        'Company Full Name (Scraped)': company_full_name,
        'About Company Text': about_company_text
    }

def extract_ipo_important_dates(soup):
    """
    Extracts IPO Important Dates from the IPO detail page by targeting
    <strong> tags with core date labels (like "Opening Date") and then getting their next sibling <td>.
    This version processes the strong tag's full text content for matching, which handles
    cases like "SME IPO Issue Opening Date:" or "IPO Issue Opening Date:".
    """
    dates_data = {}
    
    # Define patterns for the core date labels.
    date_field_patterns = {
        "IPO Open Date": re.compile(r'Opening Date', re.IGNORECASE),
        "IPO Close Date": re.compile(r'Closing Date', re.IGNORECASE),
        "Basis of Allotment": re.compile(r'Basis of Allotment Date', re.IGNORECASE),
        "Initiation of Refunds": re.compile(r'Refunds Initiation', re.IGNORECASE),
        "Credit of Shares to Demat": re.compile(r'Credit of Shares to Demat', re.IGNORECASE),
        "Listing Date": re.compile(r'Listing Date', re.IGNORECASE), 
    }

    all_strong_tags = soup.find_all('strong')

    for output_key, pattern in date_field_patterns.items():
        found = False
        for strong_tag in all_strong_tags:
            strong_text = clean_text(strong_tag.get_text())
            
            if pattern.search(strong_text):
                target_td = strong_tag.find_parent('td')
                if target_td:
                    value_td = target_td.find_next_sibling('td')
                    if value_td:
                        value = clean_text(value_td.get_text(strip=True))
                        dates_data[output_key] = value
                        found = True
                        break # Break from inner loop once found for this key
        
    for key in date_field_patterns.keys():
        if key not in dates_data:
            dates_data[key] = 'N/A'
    
    return dates_data

def extract_ipo_other_details(soup):
    """
    Extracts various IPO details from the first table within the specific div.
    """
    other_details = {}
    print("DEBUG: Starting extract_ipo_other_details function======" , other_details)
    # Check if the soup object is valid
    if not soup or not isinstance(soup, BeautifulSoup):
        print("DEBUG: Invalid soup object provided.")
        return {
            "IPO Issue Price": "N/A", "DRHP (url)": "N/A", "RHP-url": "N/A", "Anchor list-url": "N/A",
            "Retail Quota": "N/A", "IPO Issue Type": "N/A", "IPO Issue Size": "N/A", "Fresh Issue": "N/A",
            "Face Value": "N/A", "Promoter Holding Pre IPO": "N/A", "Promoter Holding Post IPO": "N/A",
            "IPO Issue Opening Date": "N/A", "IPO Issue Closing Date": "N/A",
        }
    print("DEBUG: Soup object is valid, proceeding with extraction.")



    all_tables_with_class = soup.find_all('table', class_=['table', 'table-bordered', 'table-striped', 'table-hover', 'w-auto'])
    print(f"DEBUG: Found {len(all_tables_with_class)} tables with the target classes on the page.")

    # get frist table with the target classes
    if not all_tables_with_class:
        print("DEBUG: No tables found with the target classes.")
        return {
            "IPO Issue Price": "N/A", "DRHP (url)": "N/A", "RHP-url": "N/A", "Anchor list-url": "N/A",
            "Retail Quota": "N/A", "IPO Issue Type": "N/A", "IPO Issue Size": "N/A", "Fresh Issue": "N/A",
            "Face Value": "N/A", "Promoter Holding Pre IPO": "N/A", "Promoter Holding Post IPO": "N/A",
            "IPO Issue Opening Date": "N/A", "IPO Issue Closing Date": "N/A",
        }
    print("DEBUG: Found tables with target classes, proceeding to find the specific IPO Details table.")
    # Find the first table with the target classes
    # Note: The original code was looking for a specific table, but we will now look for the first one
    # that contains the "IPO Details" header in the first column.
    first_table = all_tables_with_class[0]
    print(f"DEBUG: Using first table found: {first_table}")
    # Check if the first table has the expected structure
    if not first_table or not first_table.find('thead'):
        print("DEBUG: First table does not have the expected structure.")
        return {
            "IPO Issue Price": "N/A", "DRHP (url)": "N/A", "RHP-url": "N/A", "Anchor list-url": "N/A",
            "Retail Quota": "N/A", "IPO Issue Type": "N/A", "IPO Issue Size": "N/A", "Fresh Issue": "N/A",
            "Face Value": "N/A", "Promoter Holding Pre IPO": "N/A", "Promoter Holding Post IPO": "N/A",
            "IPO Issue Opening Date": "N/A", "IPO Issue Closing Date": "N/A",
        }
    print("DEBUG: First table has the expected structure, proceeding to find the target column div.")

    #under geted frist table, find the target we also check that we have the frist <tbody><tr><td><strong>IPO<!-- --> Issue Opening Date: </strong> the frist strong tag i slike that so we can scrap that data.  also if we cant get in to frist tale so we can for nect
    # Find the first <tbody> and then the first <tr> with a <td> that has a <strong> tag containing "IPO Issue Opening Date"
    target_td = first_table.find('td', string=re.compile(r'IPO\s+Issue\s+Opening\s+Date', re.IGNORECASE))
    if not target_td:
        print("DEBUG: Could not find the target <td> with 'IPO Issue Opening Date' in the first table.")
        return {
            "IPO Issue Price": "N/A", "DRHP (url)": "N/A", "RHP-url": "N/A", "Anchor list-url": "N/A",
            "Retail Quota": "N/A", "IPO Issue Type": "N/A", "IPO Issue Size": "N/A", "Fresh Issue": "N/A",
            "Face Value": "N/A", "Promoter Holding Pre IPO": "N/A", "Promoter Holding Post IPO": "N/A",
            "IPO Issue Opening Date": "N/A", "IPO Issue Closing Date": "N/A", 
          }
    print("DEBUG: Found the target <td> with 'IPO Issue Opening Date' in the first table.")
    #   # Now, we will find the parent div that contains the h2 with "IPO Details" to ensure we are in the right section.  
    # Find the parent div of the target <td>
    # target_div = target_td.find_parent('div', class_=['col-lg-6', 'col-md-6', 'col-sm-12'])
    # Find the parent div: col-lg-6 col-md-6 col-sm-12 that contains the h2 with "IPO Details"
    target_col_div = None
    for div in soup.find_all('div', class_=['col-lg-6', 'col-md-6', 'col-sm-12']):
        h2_tag = div.find('h2', itemprop='about', string=re.compile(r'IPO\s+Details', re.IGNORECASE))
        if h2_tag:
            target_col_div = div
            print("DEBUG: Found the target column div for IPO Details table.")
            break

    if not target_col_div:
        print("DEBUG: Could not find the target column div for IPO Details table.")
        return {
            "IPO Issue Price": "N/A", "DRHP (url)": "N/A", "RHP-url": "N/A", "Anchor list-url": "N/A",
            "Retail Quota": "N/A", "IPO Issue Type": "N/A", "IPO Issue Size": "N/A", "Fresh Issue": "N/A",
            "Face Value": "N/A", "Promoter Holding Pre IPO": "N/A", "Promoter Holding Post IPO": "N/A",
            "IPO Issue Opening Date": "N/A", "IPO Issue Closing Date": "N/A",
        }

    # Find the table within this div
    all_tables_with_class = soup.find_all('table', class_=['table', 'table-bordered', 'table-striped', 'table-hover', 'w-auto'])
    print(f"DEBUG: Found {len(all_tables_with_class)} tables with the target classes on the page.")

    details_table = target_col_div.find('table', class_=['table', 'table-bordered', 'table-striped', 'table-hover', 'w-auto'])
    print(f"DEBUG: Found details table: {details_table is not None}")

    if not details_table:
        print("DEBUG: Could not find the IPO Details table within the target div.")
        return {
            "IPO Issue Price": "N/A", "DRHP (url)": "N/A", "RHP-url": "N/A", "Anchor list-url": "N/A",
            "Retail Quota": "N/A", "IPO Issue Type": "N/A", "IPO Issue Size": "N/A", "Fresh Issue": "N/A",
            "Face Value": "N/A", "Promoter Holding Pre IPO": "N/A", "Promoter Holding Post IPO": "N/A",
            "IPO Issue Opening Date": "N/A", "IPO Issue Closing Date": "N/A",
        }

    # Define a mapping from cleaned label text to output key
    label_to_key_map = {
        "ipo issue opening date": "IPO Issue Opening Date",
        "ipo issue closing date": "IPO Issue Closing Date",
        "ipo issue price": "IPO Issue Price",
        "drhp": "DRHP (url)",
        "rhp": "RHP-url",
        "anchor list": "Anchor list-url",
        "retail quota": "Retail Quota",
        "ipo issue type": "IPO Issue Type",
        "ipo issue size": "IPO Issue Size",
        "fresh issue": "Fresh Issue",
        "face value": "Face Value",
        "promoter holding pre ipo": "Promoter Holding Pre IPO",
        "promoter holding post ipo": "Promoter Holding Post IPO",
    }

    rows = details_table.find_all('tr')
    print(f"DEBUG: Found {len(rows)} rows in the IPO Details table.")
    for row_idx, row in enumerate(rows):
        cols = row.find_all('td')
        if len(cols) == 2:
            label_strong = cols[0].find('strong')
            if label_strong:
                label_raw = label_strong.get_text() # Get raw text for debugging
                label = clean_text(label_raw).lower() # Clean and convert to lower for consistent mapping
                value_td = cols[1]
                value_raw = value_td.get_text() # Get raw value for debugging

                print(f"DEBUG: Processing row {row_idx}: Label='{label_raw}', Value='{value_raw}'")
                
                output_key = label_to_key_map.get(label)
                if output_key:
                    if "url" in output_key: # Check if it's a URL field
                        link_tag = value_td.find('a')
                        extracted_value = link_tag['href'] if link_tag and 'href' in link_tag.attrs else "N/A"
                    else:
                        extracted_value = clean_text(value_td.get_text())
                    
                    other_details[output_key] = extracted_value
                    print(f"DEBUG: Extracted '{output_key}': '{extracted_value}' from row {row_idx}.")
                else:
                    print(f"DEBUG: Unmapped label found: '{label_raw}' (cleaned: '{label}') in row {row_idx}.")
            else:
                print(f"DEBUG: No strong tag found in first column of row {row_idx}. Skipping row.")
        else:
            print(f"DEBUG: Row {row_idx} does not have 2 columns (td tags). Skipping row.")

    # Ensure all keys are present, even if N/A
    for key in label_to_key_map.values(): # Use values from the map to ensure all expected keys are present
        if key not in other_details:
            other_details[key] = "N/A"
            print(f"DEBUG: Key '{key}' not found in table, set to 'N/A'.")

    return other_details

def extract_summary_block_details(soup):
    """
    Extracts IPO Summary Text and minimum lot size (shares per lot) 
    from the div with class 'float-none mb-2 ms-2'.
    """
    summary_details = {
        'Min Order Quantity (Scraped)': '1 lot',  # Most cases assume 1 lot
        'Shares Per Lot (Scraped)': 'N/A',
        'IPO Summary Text': 'N/A'
    }

    div_logo = soup.find('div', class_='div-logo')
    target_div = None

    if div_logo:
        target_div = div_logo.find_next_sibling('div', class_=['float-none', 'mb-2', 'ms-2'])

    if target_div:
        ipo_summary_paragraphs = []
        for p_tag in target_div.find_all('p'):
            paragraph_text = clean_text(p_tag.get_text())
            if paragraph_text:
                ipo_summary_paragraphs.append(paragraph_text)

        if ipo_summary_paragraphs:
            full_summary_text = "\n\n".join(ipo_summary_paragraphs)
            summary_details['IPO Summary Text'] = full_summary_text

            # Regex to find lot size: "comprising 211 shares", etc.
            match = re.search(r'comprising\s+(\d+)\s+shares', full_summary_text, re.IGNORECASE)
            if match:
                summary_details['Shares Per Lot (Scraped)'] = match.group(1)
            else:
                print("DEBUG: Lot size not found in summary text.")

        else:
            print("DEBUG: No paragraphs found within the target summary div.")
    else:
        print("DEBUG: Target div for IPO Summary Text was not found.")

    return summary_details


def parse_date_status(date_string):
    """
    Attempts to parse date and determine if it's past, present, or future.
    Handles ordinal suffixes (st, nd, rd, th) in dates.
    Returns tuple: (parsed_date, status, original_string)
    """
    if not date_string or date_string == 'N/A':
        return None, 'Unknown', date_string
    
    # Remove ordinal suffixes (st, nd, rd, th) before parsing
    cleaned_date_string = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_string, flags=re.IGNORECASE)

    # Common date formats to try after cleaning
    date_formats_to_try = [
        '%d %b %Y',     # e.g., "3 Jul 2025"
        '%d %B %Y',     # e.g., "3 July 2025"
        '%d/%m/%Y',     # e.g., "03/07/2025"
        '%d-%m-%Y',     # e.g., "03-07-2025"
        '%B %d, %Y',    # e.g., "July 3, 2025"
        '%b %d, %Y',    # e.g., "Jul 3, 2025"
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


def scrape_full_ipo_details_from_pages(base_url="https://www.investorgain.com"):
    """
    Main function to scrape comprehensive IPO details including important dates,
    company full name, 'About Company' text, and various issue details from IPO detail pages.
    """
    all_ipo_data = []

    print("Fetching IPO list from API...")
    ipo_list = fetch_ipo_list_from_api()
    if not ipo_list:
        print("No IPOs found or error fetching IPO list. Exiting.")
        return []

    print(f"Found {len(ipo_list)} IPOs via API. Starting detailed page scraping...")

    for i, ipo_entry in enumerate(ipo_list, 1):
        # Extract initial details from API response
        ipo_id = ipo_entry.get('id')
        company_short_name_api = ipo_entry.get('company_short_name') # Renamed to differentiate
        url_rewrite_folder_name = ipo_entry.get('urlrewrite_folder_name')
        ipo_category = ipo_entry.get('ipo_category')
        
        # Initialize with API data, marking as "from API" where relevant
        current_ipo_data = {
            'IPO ID': ipo_id,
            'Company Short Name (from API)': company_short_name_api,
            'IPO Category (from API)': ipo_category,
            'Detail URL': f"{base_url}/ipo/{url_rewrite_folder_name}/{ipo_id}/",
            'Scraping Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            # Initialize with N/A for fields we'll attempt to scrape or for those
            # that might be missing from API consistently.
            'Company Full Name (Scraped)': 'N/A',
            'About Company Text': 'N/A',
            'Issue Size (Cr)': ipo_entry.get('issue_size', 'N/A'), # Keep API value, will be overwritten if scraped
            'Issue Price Band': ipo_entry.get('issue_price', 'N/A'), # Same here
            'Min Order Quantity': ipo_entry.get('min_order_quantity', 'N/A'), # Will be overwritten by scraped if found
            'Lot Size': ipo_entry.get('lot_size', 'N/A'), # Will be overwritten by scraped if found
            'Listing On': ipo_entry.get('listing_on', 'N/A'),
            'Issue Type': ipo_entry.get('issue_type', 'N/A'),
            'Face Value': ipo_entry.get('face_value', 'N/A'),
            'QIB Allotment %': ipo_entry.get('qib_allotment_percent', 'N/A'),
            'HNI Allotment %': ipo_entry.get('hni_allotment_percent', 'N/A'),
            'Retail Allotment %': ipo_entry.get('retail_allotment_percent', 'N/A'),
            'Registrar Name': ipo_entry.get('registrar_name', 'N/A'),
            'Lead Managers': ipo_entry.get('lead_managers', 'N/A'),
            'Bankers': ipo_entry.get('bankers', 'N/A'),
            'Auditors': ipo_entry.get('auditors', 'N/A'),
            'Shares Per Lot (Scraped)': 'N/A', # NEW field
            'IPO Summary Text': 'N/A' # NEW field
        }


        # Skip if essential URL components are missing
        if not url_rewrite_folder_name or not ipo_id:
            print(f"[{i}/{len(ipo_list)}] Skipping {company_short_name_api} - missing URL data")
            all_ipo_data.append(current_ipo_data) # Append partial data
            continue

        detail_url = current_ipo_data['Detail URL'] # Use the constructed URL

        print(f"[{i}/{len(ipo_list)}] Processing: {company_short_name_api}")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        try:
            response = requests.get(detail_url, headers=headers, timeout=15)
            response.raise_for_status() # Check for HTTP errors (404, 500, etc.)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # --- Extract data from detail page ---
            # important_dates_scraped = extract_ipo_important_dates(soup)
            # company_about_details_scraped = extract_company_about(soup)
            ipo_other_details_scraped = extract_ipo_other_details(soup) # NEW: Scrape other IPO details
            # summary_block_details_scraped = extract_summary_block_details(soup) # Scrape summary block details
            
            # --- Update combined data with scraped values ---
            # current_ipo_data.update(important_dates_scraped)
            # current_ipo_data.update(company_about_details_scraped)
            current_ipo_data.update(ipo_other_details_scraped) # Add new other IPO details
            # current_ipo_data.update(summary_block_details_scraped) # Add new summary block details

            # --- Add parsed date status for key dates ---
            key_dates_for_status = ['IPO Issue Opening Date', 'IPO Issue Closing Date', 'Listing Date']
            for key in key_dates_for_status:
                if key in current_ipo_data: # Check in combined data now
                    parsed_date, status, original = parse_date_status(current_ipo_data[key])
                    current_ipo_data[f'{key} Status'] = status
                    if parsed_date:
                        current_ipo_data[f'{key} Parsed'] = parsed_date.strftime('%Y-%m-%d')
                    else:
                        current_ipo_data[f'{key} Parsed'] = 'N/A'
            
            all_ipo_data.append(current_ipo_data)
            
            # Provide feedback on what was found
            found_company_full_name = "Yes" if current_ipo_data.get('Company Full Name (Scraped)') != 'N/A' else "No"
            found_text_summary = "Yes" if current_ipo_data.get('IPO Summary Text') != 'N/A' else "No"
            found_issue_price = "Yes" if current_ipo_data.get('IPO Issue Price') != 'N/A' else "No"
            # print(f"    ✓ Scraped Company Full Name: {found_company_full_name}, Summary Text: {found_text_summary}, Issue Price: {found_issue_price}.")

        except requests.exceptions.RequestException as e:
            print(f"    ✗ Network error for {detail_url}: {e}")
            all_ipo_data.append(current_ipo_data) # Append partial data even on error
        except Exception as e:
            print(f"    ✗ Parsing error for {detail_url}: {e}")
            all_ipo_data.append(current_ipo_data) # Append partial data even on error

        # Be polite and avoid overwhelming the server
        time.sleep(1.5)

    return all_ipo_data

def save_to_json(data, filename="ipo_detailed_data.json"): # New default filename
    """
    Saves the scraped IPO data to a JSON file.
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"✓ Data saved to JSON: {filename}")
    except IOError as e:
        print(f"✗ Error saving JSON: {e}")

def print_summary(data):
    """
    Prints a summary of the scraped IPO data.
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
        # Check if IPO has meaningful date data (not all N/A for key fields)
        has_dates = any(ipo.get(key, 'N/A') != 'N/A' for key in ['IPO Open Date', 'IPO Close Date', 'Listing Date'])
        if has_dates:
            ipos_with_dates += 1
        
        # Determine IPO status based on parsed date statuses
        open_status = ipo.get('IPO Open Date Status', 'Unknown')
        close_status = ipo.get('IPO Close Date Status', 'Unknown')
        
        if open_status == 'Future':
            upcoming_ipos += 1
        # An IPO is ongoing if it opened (today or in past) and hasn't closed yet (today or in future)
        elif open_status in ['Today', 'Past'] and close_status in ['Future', 'Today']:
            ongoing_ipos += 1
        elif close_status == 'Past':
            completed_ipos += 1
    
    print(f"\n=== IPO DATA SUMMARY (from Detail Pages) ===")
    print(f"Total IPOs Processed: {total_ipos}")
    print(f"IPOs with any key date information: {ipos_with_dates}")
    print(f"Upcoming IPOs (Open Date in Future): {upcoming_ipos}")
    print(f"Ongoing IPOs (Open Today/Past, Close Today/Future): {ongoing_ipos}")
    print(f"Completed IPOs (Close Date in Past): {completed_ipos}")
    
    if total_ipos > 0:
        print(f"Data Success Rate (IPOs with key dates): {(ipos_with_dates/total_ipos)*100:.1f}%")
    else:
        print("Data Success Rate: N/A (No IPOs scraped)")

if __name__ == "__main__":
    print("=== IPO Detailed Scraper (Combining API & Web Scraping) ===")
    print("This script first fetches basic IPO data from an API and then enriches it by scraping")
    print("missing or detailed information (About Company, Issue Size, Price Band, etc.)")
    print("from individual IPO detail pages on Investorgain.com.")
    print("Output will be saved to 'ipo_detailed_data.json'.")
    
    print("\nStarting scraping process...")
    # Call the main scraping function
    ipo_detailed_data = scrape_full_ipo_details_from_pages()
    
    if ipo_detailed_data:
        # Save the collected data to a JSON file
        save_to_json(ipo_detailed_data)
        
        # Print a summary of the scraped data
        print_summary(ipo_detailed_data)
        
        # Show sample data for the first IPO
        print(f"\n=== SAMPLE DATA (First IPO) ===")
        if len(ipo_detailed_data) > 0:
            sample = ipo_detailed_data[0]
            for key, value in sample.items():
                # For long text fields like 'About Company Text', print only a snippet
                if key == 'About Company Text' and len(str(value)) > 200: # Limit to 200 chars for display
                    print(f"{key}: {str(value)[:200]}...")
                elif key == 'IPO Summary Text' and len(str(value)) > 200:
                    print(f"{key}: {str(value)[:200]}...")
                elif key == 'Company Full Name (Scraped)' and len(str(value)) > 50:
                    print(f"{key}: {str(value)[:50]}...")
                else:
                    print(f"{key}: {value}")
                
        # Show a summary of upcoming IPOs
        upcoming = [ipo for ipo in ipo_detailed_data if ipo.get('IPO Open Date Status') == 'Future']
        if upcoming:
            print(f"\n=== FIRST 5 UPCOMING IPOs ===")
            for ipo in upcoming[:5]: # Display details for the first 5 upcoming IPOs
                print(f"- {ipo.get('Company Short Name (from API)', 'N/A')} (Category: {ipo.get('IPO Category (from API)', 'N/A')}), Opens: {ipo.get('IPO Open Date', 'N/A')}, Issue Size: {ipo.get('Issue Size (Cr)', 'N/A')}")
        else:
            print("\nNo upcoming IPOs found in the scraped data.")
    else:
        print("No data was scraped.")
    
    print("\n=== Scraping Complete ===")


