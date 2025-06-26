import requests
from bs4 import BeautifulSoup
import json
import time
import re
import datetime # Added for dynamic filename generation
import traceback # Added for more detailed error logging

# Base URLs
IPO_LIST_API_URL = "https://webnodejs.investorgain.com/cloud/ipo/list-read"
IPO_DETAIL_BASE_URL = "https://www.investorgain.com/ipo/"

# Custom User-Agent to mimic a browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def fetch_ipo_list():
    """
    Fetches the list of current IPOs from the Investorgain API.
    Returns:
        list: A list of dictionaries, each representing an IPO summary.
    """
    print(f"Fetching IPO list from: {IPO_LIST_API_URL}")
    try:
        response = requests.get(IPO_LIST_API_URL, headers=HEADERS)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        if data.get("msg") == 1 and data.get("ipoList"):
            print(f"Successfully fetched {len(data['ipoList'])} IPOs.")
            return data["ipoList"]
        else:
            print("Failed to retrieve IPO list or empty list received.")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Error fetching IPO list: {e}")
        return []

def extract_key_value_table(table_soup):
    """
    Extracts data from tables where the first column is the key and the second is the value.
    Handles links in the value column.
    """
    data = {}
    if not table_soup:
        print("Debug: extract_key_value_table received empty table_soup")
        return data

    # Try to find tbody, if not found, search tr directly under the table
    rows = table_soup.find('tbody').find_all('tr') if table_soup.find('tbody') else table_soup.find_all('tr')
    print(f"Debug: Found {len(rows)} rows in extract_key_value_table")

    for row in rows:
        cols = row.find_all(['td', 'th']) # Check both td and th for robustness
        if len(cols) == 2:
            key = cols[0].get_text(strip=True).replace(':', '').replace('*', '').strip()
            link_tag = cols[1].find('a', href=True)
            if link_tag and 'href' in link_tag.attrs:
                value = link_tag['href']
            else:
                value = cols[1].get_text(strip=True)
            data[key] = value
            print(f"Debug: Extracted key-value: {key} = {value}")
    return data

def parse_table_to_dict(table_element):
    """
    Parses an HTML table into a list of dictionaries.
    Assumes the first row is the header if no <thead>, otherwise uses <thead>.
    """
    headers = []
    # Try to find headers in <thead> first
    thead = table_element.find('thead')
    if thead:
        header_rows = thead.find_all('tr')
        for hr in header_rows:
            ths = hr.find_all(['th', 'td'])
            if ths: # Ensure there are headers in this row
                headers = [th.get_text(strip=True) for th in ths]
                break # Take the first non-empty header row found
    
    # Fallback to first <tbody> row if no <thead> or empty <thead>
    # Also handle cases where the first row in tbody might be a header-like row
    data_rows = []
    tbody = table_element.find('tbody')
    if tbody:
        data_rows = tbody.find_all('tr')

    if not headers and data_rows:
        # Assume first row of tbody is header if no thead
        first_row_cells = data_rows[0].find_all(['th', 'td'])
        headers = [th.get_text(strip=True) for th in first_row_cells]
        # Remove the first row from data_rows as it's now considered headers
        data_rows = data_rows[1:]

    # Filter out empty headers and clean them up
    headers = [h for h in headers if h] # Remove empty strings
    # Simple cleanup for special characters in headers if needed
    headers = [re.sub(r'[^a-zA-Z0-9\s%]', '', h).strip() for h in headers]
    print(f"Debug: Parsed headers: {headers}")
    
    table_data = []
    
    for row in data_rows:
        cells = row.find_all(['td', 'th'])
        row_data = {}
        for i, cell in enumerate(cells):
            if i < len(headers):
                text = cell.get_text(strip=True).replace('\n', ' ').replace('\t', '')
                row_data[headers[i]] = text
        if row_data and any(row_data.values()): # Only add if row data is not empty or all values are empty strings
            table_data.append(row_data)
            print(f"Debug: Parsed row data: {row_data}")
    return table_data

def scrape_ipo_details(ipo_url):
    """
    Scrapes detailed information for a single IPO from its dedicated page.
    Args:
        ipo_url (str): The URL of the IPO detail page.
    Returns:
        dict: A dictionary containing the scraped IPO details.
    """
    print(f"Scraping details from: {ipo_url}")
    ipo_details = {}
    try:
        response = requests.get(ipo_url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # 1. IPO Name (Title)
        ipo_name_div = soup.find("div", class_="col-lg-6")
        if ipo_name_div:
            h1_tag = ipo_name_div.find("h1")
            if h1_tag:
                # Remove specific trailing text for cleanliness
                ipo_details["IPO Name"] = h1_tag.get_text(strip=True).replace(" SME IPO Details 2025", "").replace(" IPO Details 2025", "").strip()

        # 2. IPO Logo Image
        logo_div = soup.find("div", class_="div-logo")
        if logo_div:
            logo_img_tag = logo_div.find("img")
            if logo_img_tag:
                ipo_details["IPO Logo"] = logo_img_tag.get("src", "") # Renamed key to 'IPO Logo'

        # 3. IPO Detail Paragraphs (About IPO Company Description)
        ipo_description_div = soup.find("div", class_="float-none mb-2 ms-2")
        if ipo_description_div:
            paragraphs = ipo_description_div.find_all("p")
            if paragraphs: 
                ipo_details["IPO Description"] = "\n".join([p.get_text(strip=True) for p in paragraphs])

        # 4. IPO Details Table
        # This is the first div with itemprop="http://schema.org/Table" inside the first .col-lg-6
        ipo_details_section = None
        first_col_lg_6_group = soup.find('div', class_='row g-0').find('div', class_='col-lg-6 col-md-6 col-sm-12')
        if first_col_lg_6_group:
            ipo_details_section = first_col_lg_6_group.find('div', itemprop='http://schema.org/Table')
        
        if ipo_details_section and ipo_details_section.find('h2', itemprop='about') and "IPO Details" in ipo_details_section.find('h2', itemprop='about').get_text():
            table = ipo_details_section.find('table', class_='table')
            ipo_details["IPO Details"] = extract_key_value_table(table)
        else:
            ipo_details["IPO Details"] = {}

        # Find the second col-lg-6 block for important dates and lots
        second_col_lg_6_group = None
        all_col_lg_6_groups = soup.find_all('div', class_='col-lg-6 col-md-6 col-sm-12')
        if len(all_col_lg_6_groups) > 1:
            second_col_lg_6_group = all_col_lg_6_groups[1] # This should be the one on the right

        # 5. IPO Important Dates (Table)
        important_dates_section = None
        if second_col_lg_6_group:
            important_dates_section = second_col_lg_6_group.find('div', itemprop='http://schema.org/Table')

        if important_dates_section and important_dates_section.find('h2', itemprop='about') and "IPO Important Dates" in important_dates_section.find('h2', itemprop='about').get_text():
            table = important_dates_section.find('table', class_='table')
            ipo_details["Important Dates"] = extract_key_value_table(table)
        else:
            ipo_details["Important Dates"] = {}

        # 6. IPO Lots (Table)
        ipo_lots_section = None
        if second_col_lg_6_group:
            all_tables_in_second_group = second_col_lg_6_group.find_all('div', itemprop='http://schema.org/Table')
            if len(all_tables_in_second_group) > 1:
                ipo_lots_section = all_tables_in_second_group[1]

        if ipo_lots_section and ipo_lots_section.find('h2', itemprop='about') and "IPO Lots" in ipo_lots_section.find('h2', itemprop='about').get_text():
            table = ipo_lots_section.find('table', class_='table')
            ipo_details["IPO Lots"] = extract_key_value_table(table)
        else:
            ipo_details["IPO Lots"] = {}

        # 7. IPO GMP Table
        gmp_h2 = soup.find("h2", itemprop="about", string=lambda text: text and ("SME IPO GMP**" in text or "IPO GMP**" in text))
        if gmp_h2:
            gmp_table_div = gmp_h2.find_next_sibling("div", class_="table-responsive")
            if gmp_table_div:
                gmp_table = gmp_table_div.find("table")
                if gmp_table:
                    ipo_details["IPO GMP"] = parse_table_to_dict(gmp_table)

        # 8. About Company - IPO Company Details Paragraphs
        about_company_h3 = soup.find("h3", itemprop="about", string=lambda text: text and "About Company -" in text)
        if about_company_h3:
            about_company_div = about_company_h3.find_next_sibling("div")
            if about_company_div:
                paragraphs = about_company_div.find_all("p")
                if paragraphs:
                    ipo_details["About Company"] = "\n".join([p.get_text(strip=True) for p in paragraphs])

        # 9. IPO Strengths
        strengths_h3 = soup.find("h3", string=lambda text: text and ("SME IPO Strengths" in text or "IPO Strengths" in text))
        if strengths_h3:
            strengths_div = strengths_h3.find_next_sibling("div")
            if strengths_div:
                strengths_list = [li.get_text(strip=True) for li in strengths_div.find_all("li")]
                if strengths_list:
                    ipo_details["Strengths"] = strengths_list

        # 10. Company General Information Table (Incorporation, Sector, IPO Issue Size, Website)
        strengths_h3 = soup.find("h3", string=lambda text: text and ("SME IPO Strengths" in text or "IPO Strengths" in text))
        if strengths_h3:
            # The general info table is in a table-responsive div after the strengths div
            general_info_table_div = strengths_h3.find_next_sibling("div").find_next_sibling("div", class_="table-responsive")
            if general_info_table_div:
                general_info_table = general_info_table_div.find("table")
                if general_info_table:
                    ipo_details["General Information"] = parse_table_to_dict(general_info_table)

        # 11. IPO Objective
        objective_h3 = soup.find("h3", string=lambda text: text and ("SME IPO Objective" in text or "IPO Objective" in text))
        if objective_h3:
            objective_div = objective_h3.find_next_sibling("div")
            if objective_div:
                objective_table = objective_div.find("table", id="ObjectiveIssue")
                if objective_table:
                    ipo_details["Objective"] = parse_table_to_dict(objective_table)

        # 12. Live Subscription Summary (QIB, NII, RII percentages)
        subscription_h2 = soup.find("h2", itemprop="about", string=lambda text: text and ("SME IPO Live Subscription" in text or "IPO Live Subscription" in text))
        if subscription_h2:
            # The ul is a sibling to the biddingDetails div (which is often empty)
            ul_tag_parent = subscription_h2.find_next_sibling("div", id="biddingDetails")
            if ul_tag_parent:
                ul_tag = ul_tag_parent.find_next_sibling("div") # This div contains the ul
                if ul_tag:
                    ul_element = ul_tag.find("ul")
                    if ul_element:
                        items = [li.get_text(strip=True) for li in ul_element.find_all("li")]
                        summary_data = {}
                        for item in items:
                            parts = item.split(":")
                            if len(parts) == 2:
                                key = parts[0].strip()
                                value = parts[1].strip()
                                summary_data[key] = value
                        if summary_data:
                            ipo_details["Live Subscription Summary"] = summary_data

        # 13. IPO Bidding Live Updates Table
        bidding_table_caption = soup.find("caption", string=lambda text: text and "IPO Bidding Live Updates" in text)
        if bidding_table_caption:
            bidding_table = bidding_table_caption.find_parent("table")
            if bidding_table:
                ipo_details["Bidding Live Updates"] = parse_table_to_dict(bidding_table)

        # 14. Company Financial Information (Restated) Table
        financial_h2 = soup.find("h2", itemprop="about", string=lambda text: text and ("Financial Information (Restated)" in text))
        if financial_h2:
            financial_table_div = financial_h2.find_next_sibling("div", class_="table-responsive")
            if financial_table_div:
                financial_table = financial_table_div.find("table", id="financialTable")
                if financial_table:
                    financial_data = []
                    tbody = financial_table.find("tbody")
                    if tbody:
                        rows = tbody.find_all("tr")
                        if rows:
                            period_row_cells = rows[0].find_all("td")
                            column_headers = [td.get_text(strip=True) for td in period_row_cells]

                            for row in rows[1:]:
                                cells = row.find_all("td")
                                if cells and len(cells) == len(column_headers):
                                    row_dict = {}
                                    for i, cell in enumerate(cells):
                                        if i < len(column_headers):
                                            row_dict[column_headers[i]] = cell.get_text(strip=True)
                                    if row_dict:
                                        financial_data.append(row_dict)
                    if financial_data:
                        ipo_details["Financial Information (Restated)"] = financial_data

        # 15. IPO Peer Comparison Table
        peer_comparison_h2 = soup.find("h2", itemprop="about", string=lambda text: text and ("SME IPO Peer Comparison" in text or "IPO Peer Comparison" in text))
        if peer_comparison_h2:
            next_p_peer = peer_comparison_h2.find_next_sibling("p")
            peer_table_div = None
            if next_p_peer:
                peer_table_div = next_p_peer.find_next_sibling("div", class_="table-responsive")

            if not peer_table_div:
                peer_table_div = peer_comparison_h2.find_next_sibling("div", class_="table-responsive")

            if peer_table_div:
                peer_table = peer_table_div.find("table")
                if peer_table:
                    ipo_details["Peer Comparison"] = parse_table_to_dict(peer_table)

        # 16. Contact & Management Details (Company Address, IPO Registrar, IPO Lead Manager)
        contact_details = {}

        # Company Address
        company_address_card_header = soup.find("div", class_="card-header", string=lambda text: text and "Company Address" in text)
        if company_address_card_header:
            card_body = company_address_card_header.find_next_sibling("div", class_="card-body")
            if card_body:
                text_content = card_body.get_text(separator="\n", strip=True)
                address_lines = [line.strip() for line in text_content.split('\n') if line.strip()]

                company_address = {
                    "Name": address_lines[0] if address_lines else "",
                    "Address": "\n".join(address_lines[1:]) if len(address_lines) > 1 else "",
                    "Website": "",
                    "Phone": "",
                    "Email": ""
                }

                website_match = re.search(r"Website:\s*(https?://\S+)", text_content)
                if website_match:
                    company_address["Website"] = website_match.group(1)
                phone_match = re.search(r"Phone:\s*([+\d\s-]+)", text_content)
                if phone_match:
                    company_address["Phone"] = phone_match.group(1)
                email_match = re.search(r"Email:\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", text_content)
                if email_match:
                    company_address["Email"] = email_match.group(1)
                contact_details["Company Address"] = company_address

        # IPO Registrar
        ipo_registrar_card_header = soup.find("div", class_="card-header", string=lambda text: text and "SME IPO Registrar" in text)
        if ipo_registrar_card_header:
            card_body = ipo_registrar_card_header.find_next_sibling("div", class_="card-body")
            if card_body:
                text_content = card_body.get_text(separator="\n", strip=True)
                registrar_lines = [line.strip() for line in text_content.split('\n') if line.strip()]

                ipo_registrar = {
                    "Name": registrar_lines[0] if registrar_lines else "",
                    "Address": "\n".join(registrar_lines[1:]) if len(registrar_lines) > 1 else "",
                    "Website": "",
                    "Phone": "",
                    "Email": ""
                }

                website_match = re.search(r"Website:\s*(https?://\S+)", text_content)
                if website_match:
                    ipo_registrar["Website"] = website_match.group(1)
                phone_match = re.search(r"Phone:\s*([+\d\s-]+)", text_content)
                if phone_match:
                    ipo_registrar["Phone"] = phone_match.group(1)
                email_match = re.search(r"Email:\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", text_content)
                if email_match:
                    ipo_registrar["Email"] = email_match.group(1)
                contact_details["IPO Registrar"] = ipo_registrar

        # IPO Lead Manager
        ipo_lead_manager_card_header = soup.find("div", class_="card-header", string=lambda text: text and "SME IPO Lead Manager" in text)
        if ipo_lead_manager_card_header:
            card_body = ipo_lead_manager_card_header.find_next_sibling("div", class_="card-body")
            if card_body:
                lead_managers = [li.get_text(strip=True) for li in card_body.find_all("li")]
                if lead_managers:
                    contact_details["IPO Lead Manager"] = lead_managers

        if contact_details:
            ipo_details["Contact & Management Details"] = contact_details

        # 17. Last Updated Date/Time
        last_updated_div = soup.find("div", class_="float-end my-2")
        if last_updated_div:
            p_tag = last_updated_div.find("p")
            if p_tag:
                ipo_details["Last Updated"] = p_tag.get_text(strip=True).replace("Last Updated on ", "").strip()

        return ipo_details

    except requests.exceptions.RequestException as e:
        print(f"Error fetching IPO details from {ipo_url}: {e}")
        return {}
    except Exception as e:
        print(f"An unexpected error occurred during scraping {ipo_url}: {e}")
        traceback.print_exc() # Print full traceback for debugging
        return {}

def main():
    all_ipo_data = []
    ipo_list = fetch_ipo_list()

    if ipo_list:
        for i, ipo_summary in enumerate(ipo_list):
            ipo_id = ipo_summary.get("id")
            url_rewrite_folder_name = ipo_summary.get("urlrewrite_folder_name")
            
            if ipo_id and url_rewrite_folder_name:
                detail_url = f"{IPO_DETAIL_BASE_URL}{url_rewrite_folder_name}/{ipo_id}/"
                
                detailed_ipo_info = scrape_ipo_details(detail_url)
                
                # Merge summary info with detailed info, ensuring keys match desired output
                merged_info = {
                    "id": ipo_summary.get("id"),
                    "company_short_name": ipo_summary.get("company_short_name"),
                    "issue_size": ipo_summary.get("issue_size"),
                    "issue_open_dt": ipo_summary.get("issue_open_dt"),
                    "issue_end_dt": ipo_summary.get("issue_end_dt"),
                    "listing_at": ipo_summary.get("listing_at"),
                    "urlrewrite_folder_name": ipo_summary.get("urlrewrite_folder_name"),
                    "urlrewrite_folder_name_main": ipo_summary.get("urlrewrite_folder_name_main"),
                    "ipo_status": ipo_summary.get("ipo_status"),
                    "ipo_category": ipo_summary.get("ipo_category"),
                    "orderdate": ipo_summary.get("orderdate"),
                    "orderdate_dateformat": ipo_summary.get("orderdate_dateformat"),
                    "class_ipo_status": ipo_summary.get("class_ipo_status"),
                    # Detailed info from scraping, with key mapping
                    "IPO Name": detailed_ipo_info.get("IPO Name", ""),
                    "IPO Logo": detailed_ipo_info.get("IPO Logo", ""),
                    "IPO Description": detailed_ipo_info.get("IPO Description", ""),
                    "IPO Details": detailed_ipo_info.get("IPO Details", {}),
                    "Important Dates": detailed_ipo_info.get("Important Dates", []),
                    "IPO Lots": detailed_ipo_info.get("IPO Lots", []),
                    "IPO GMP": detailed_ipo_info.get("IPO GMP", []),
                    "About Company": detailed_ipo_info.get("About Company", ""),
                    "Strengths": detailed_ipo_info.get("Strengths", []),
                    "General Information": detailed_ipo_info.get("General Information", []), # This is a list of dicts from parse_table_to_dict
                    "Objective": detailed_ipo_info.get("Objective", []),
                    "Live Subscription Summary": detailed_ipo_info.get("Live Subscription Summary", {}),
                    "Bidding Live Updates": detailed_ipo_info.get("Bidding Live Updates", []),
                    "Financial Information (Restated)": detailed_ipo_info.get("Financial Information (Restated)", []),
                    "Peer Comparison": detailed_ipo_info.get("Peer Comparison", []),
                    "Contact & Management Details": detailed_ipo_info.get("Contact & Management Details", {}),
                    "Last Updated": detailed_ipo_info.get("Last Updated", "")
                }
                all_ipo_data.append(merged_info)
                
                print(f"Scraped {i+1}/{len(ipo_list)} IPOs. Waiting for a moment...")
                time.sleep(1) # Be polite and wait for 1 second between requests

    # Output the collected data as JSON file
    current_date = datetime.datetime.now().strftime("%d-%m-%Y")
    output_filename = f"{current_date}_ipo_data.json"
    
    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(all_ipo_data, f, indent=2, ensure_ascii=False)
        print(f"\n--- All Scraped IPO Data successfully saved to {output_filename} ---")
    except IOError as e:
        print(f"Error saving data to file {output_filename}: {e}")
    
    # Also print to console for immediate feedback
    print("\n--- All Scraped IPO Data (JSON Output to Console) ---")
    import sys
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError: # For older Python versions that don't have reconfigure
        pass
    print(json.dumps(all_ipo_data, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()



