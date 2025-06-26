# html_scraper.py
# This script contains functions for scraping detailed IPO data from web pages (HTML).

import requests
from bs4 import BeautifulSoup
import json
import time
import re   # For regular expressions, especially for cleaning text

from utils import normalize_company_name, parse_flexible_date # Assuming utils.py is in the same directory

def fetch_html_content(url, headers=None, delay=1):
    """
    Fetches the HTML content of a given URL.
    
    Args:
        url (str): The URL of the web page to fetch.
        headers (dict, optional): Custom HTTP headers to send with the request.
        delay (int): Delay in seconds before fetching to prevent rate limiting.
    
    Returns:
        str or None: The HTML content as a string if successful, None otherwise.
    """
    if headers is None:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1"
        }
    
    print(f"\n[HTML Scraper] Waiting for {delay} seconds before fetching {url}...")
    time.sleep(delay) # Be polite and avoid overwhelming the server

    print(f"[HTML Scraper] Attempting to fetch HTML from: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=20) # Increased timeout
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        
        print(f"[HTML Scraper] Response Status Code: {response.status_code}")
        
        return response.text # Requests handles text decoding and decompression automatically for .text
    except requests.exceptions.HTTPError as e:
        print(f"[HTML Scraper Error] HTTP Error fetching {url}: {e}")
    except requests.exceptions.ConnectionError as e:
        print(f"[HTML Scraper Error] Connection Error fetching {url}: {e}")
    except requests.exceptions.Timeout as e:
        print(f"[HTML Scraper Error] Timeout Error fetching {url}: {e}")
    except requests.exceptions.RequestException as e:
        print(f"[HTML Scraper Error] An unexpected requests error occurred fetching {url}: {e}")
    except Exception as e:
        print(f"[HTML Scraper Error] An unhandled general error occurred in fetch_html_content for {url}: {e}")
    return None

def parse_ipo_details_from_html(html_content):
    """
    Parses specific IPO details from the HTML content of a web page
    based on the structure provided in IPO HTML scrap.txt (Investorgain.com).
    
    Args:
        html_content (str): The HTML content of the IPO detail page.
        
    Returns:
        dict: A dictionary containing the extracted IPO details.
    """
    if not html_content:
        return {}

    soup = BeautifulSoup(html_content, 'html.parser')
    ipo_details = {}

    print("[HTML Scraper] Parsing HTML content...")

    # Helper function to extract text and clean it
    def get_text_safe(element):
        if element:
            # Remove comments and normalize spaces
            text = re.sub(r'<!--.*?-->', '', element.get_text(separator=' ', strip=True))
            return text.strip().replace('\n', ' ').replace('\t', ' ')
        return ""

    # Helper function to parse a generic key-value table
    def parse_key_value_table(table_tag, heading_map=None):
        data = {}
        if table_tag:
            for row in table_tag.find_all('tr'):
                cols = row.find_all(['th', 'td'])
                if len(cols) == 2:
                    key = get_text_safe(cols[0]).replace(':', '').strip()
                    value = get_text_safe(cols[1]).strip()
                    if heading_map and key in heading_map:
                        data[heading_map[key]] = value
                    else:
                        data[key] = value
        return data

    # 1. IPO Name / Title from the page
    try:
        ipo_name_tag = soup.find('div', class_='col-lg-6').find('h1')
        if ipo_name_tag:
            ipo_details['ipo_page_title'] = get_text_safe(ipo_name_tag)
    except Exception as e:
        print(f"  Error extracting IPO Page Title: {e}")

    # 2. Basic IPO Details Paragraph (div class="float-none mb-2 ms-2")
    try:
        basic_details_div = soup.find('div', class_='float-none mb-2 ms-2')
        if basic_details_div:
            paragraphs = basic_details_div.find_all('p')
            ipo_details['basic_ipo_description_summary'] = ' '.join([get_text_safe(p) for p in paragraphs])
    except Exception as e:
        print(f"  Error extracting Basic IPO Description Summary: {e}")

    # 3. {ipo name} SME IPO Details table (main details like issue size, price, etc.)
    try:
        ipo_details_table_container = soup.find('h2', text=re.compile(r'IPO Details', re.IGNORECASE))
        if ipo_details_table_container:
            ipo_details_table = ipo_details_table_container.find_next_sibling('table', class_='table')
            if ipo_details_table:
                details_map = {
                    "SME IPO Issue Opening Date": "issue_opening_date_html",
                    "SME IPO Issue Closing Date": "issue_closing_date_html",
                    "SME IPO Issue Price": "issue_price_range_html",
                    "DRHP": "drhp_link", # These will be updated with actual links below
                    "RHP": "rhp_link", # These will be updated with actual links below
                    "IPO Listing At": "listing_at_html",
                    "Retail Quota": "retail_quota",
                    "SME IPO Issue Type": "issue_type",
                    "SME IPO Issue Size": "issue_size_html",
                    "Fresh Issue": "fresh_issue_amount_html",
                    "Face Value": "face_value",
                    "Promoter Holding Pre IPO": "promoter_holding_pre_ipo",
                    "Promoter Holding Post IPO": "promoter_holding_post_ipo",
                }
                extracted_table_data = parse_key_value_table(ipo_details_table, details_map)
                
                # Extract DRHP/RHP links specifically using data-title
                drhp_link_tag_td = ipo_details_table.find('td', {'data-title': 'Cedaar Textile\xa0IPO SME IPO DRHP'})
                if drhp_link_tag_td and drhp_link_tag_td.find('a'):
                    extracted_table_data['drhp_link'] = drhp_link_tag_td.find('a').get('href')
                
                rhp_link_tag_td = ipo_details_table.find('td', {'data-title': 'Cedaar Textile\xa0IPO SME IPO RHP'})
                if rhp_link_tag_td and rhp_link_tag_td.find('a'):
                    extracted_table_data['rhp_link'] = rhp_link_tag_td.find('a').get('href')

                ipo_details.update(extracted_table_data)
    except Exception as e:
        print(f"  Error extracting IPO Details Table: {e}")

    # 4. {IPO Name} IPO Important Dates table (Allotment, Refunds, Credit to Demat, Listing)
    try:
        important_dates_table_container = soup.find('h2', text=re.compile(r'Important Dates', re.IGNORECASE))
        if important_dates_table_container:
            important_dates_table = important_dates_table_container.find_next_sibling('table', class_='table')
            if important_dates_table:
                dates_map = {
                    "Basis of Allotment Date*": "allotment_date_html",
                    "Refunds Initiation*": "refunds_initiation_date",
                    "Credit of Shares to Demat*": "credit_to_demat_date_html",
                    "SME IPO Listing Date*": "listing_date_html_full" # Differentiated from initial API listing_date
                }
                extracted_dates = parse_key_value_table(important_dates_table, dates_map)
                ipo_details.update(extracted_dates)
    except Exception as e:
        print(f"  Error extracting Important Dates Table: {e}")
    
    # 5. {IPO Name} IPO Lots table
    try:
        lots_table_container = soup.find('h2', text=re.compile(r'IPO Lots', re.IGNORECASE))
        if lots_table_container:
            lots_table = lots_table_container.find_next_sibling('table', class_='table')
            if lots_table:
                lots_map = {
                    "Issue Price": "lot_issue_price",
                    "Market Lot:": "market_lot_shares",
                    "Individual Investor:": "individual_investor_amount",
                    "Min HNI Lots:": "min_hni_lots"
                }
                extracted_lots = parse_key_value_table(lots_table, lots_map)
                ipo_details.update(extracted_lots)
    except Exception as e:
        print(f"  Error extracting IPO Lots Table: {e}")

    # 6. {IPO name} IPO GMP (Historical GMP Table) - Section 5 in your doc
    try:
        gmp_table_container = soup.find('h2', text=re.compile(r'IPO GMP', re.IGNORECASE))
        if gmp_table_container:
            gmp_table = gmp_table_container.find_next_sibling('table', class_='table')
            if gmp_table:
                gmp_history = []
                headers = [get_text_safe(th) for th in gmp_table.find('thead').find_all('th')]
                for row in gmp_table.find('tbody').find_all('tr'):
                    row_data = [get_text_safe(td) for td in row.find_all('td')]
                    if len(headers) == len(row_data):
                        gmp_history.append(dict(zip(headers, row_data)))
                ipo_details['gmp_historical_data'] = gmp_history
    except Exception as e:
        print(f"  Error extracting GMP History Table: {e}")


    # 7. About Company - AJC Jewel (Company Overview, Strengths, Basic Info Table) - Section 6 in your doc
    try:
        about_company_h3 = soup.find('h3', text=re.compile(r'About Company', re.IGNORECASE))
        if about_company_h3:
            # Company Overview Paragraphs
            # Find the div immediately after the About Company h3 that contains <p> tags
            company_overview_content_div = about_company_h3.find_next_sibling('div') 
            if company_overview_content_div:
                paragraphs = company_overview_content_div.find_all('p')
                ipo_details['company_overview_detailed'] = ' '.join([get_text_safe(p) for p in paragraphs])
            
            # Strengths
            strengths_h3 = soup.find('h3', text=re.compile(r'Strengths', re.IGNORECASE))
            if strengths_h3:
                strengths_div = strengths_h3.find_next_sibling('div')
                if strengths_div:
                    ipo_details['company_strengths'] = [get_text_safe(li) for li in strengths_div.find_all('li')]

            # Basic Info Table (Incorporation, Sector, IPO Issue Size, Website)
            # Find the parent div of the strengths_div, then locate the table within it
            # The structure suggests the table is within a div class="table-responsive" directly sibling to a div containing paragraphs, which is itself sibling to the strengths div.
            # A more robust way might be to look for the table containing "Incorporation" etc.
            basic_info_table_container = soup.find('table', class_='table', attrs={'w-auto': True}) 
            if basic_info_table_container and basic_info_table_container.find('th', text='Incorporation'): # Check for unique header
                basic_info_map = {
                    "Incorporation": "incorporation_year",
                    "Sector": "company_sector",
                    "IPO Issue Size": "company_ipo_issue_size_info",
                    "Website": "company_website_info"
                }
                extracted_basic_info = parse_key_value_table(basic_info_table_container, basic_info_map)
                
                website_td = basic_info_table_container.find('td', string=re.compile(r'https?://'))
                if website_td and website_td.find('a'):
                    extracted_basic_info['company_website_info'] = website_td.find('a').get('href')

                ipo_details.update(extracted_basic_info)

    except Exception as e:
        print(f"  Error extracting About Company section: {e}")

    # 8. IPO Objective - Section 7 in your doc (re-indexed from your doc to match my previous category structure)
    try:
        objective_h3 = soup.find('h3', text=re.compile(r'Objective', re.IGNORECASE))
        if objective_h3:
            objective_div = objective_h3.find_next_sibling('div')
            if objective_div:
                objective_para = objective_div.find('p')
                if objective_para:
                    ipo_details['ipo_objective_overview'] = get_text_safe(objective_para)

                objective_table = objective_div.find('table', id='ObjectiveIssue')
                if objective_table:
                    objectives_list = []
                    for row in objective_table.find('tbody').find_all('tr'):
                        tds = row.find_all('td')
                        if len(tds) >= 3:
                            objectives_list.append({
                                's_no': get_text_safe(tds[0]),
                                'objective': get_text_safe(tds[1]),
                                'expected_amount_cr': get_text_safe(tds[2])
                            })
                    ipo_details['ipo_objectives_details'] = objectives_list
    except Exception as e:
        print(f"  Error extracting IPO Objective section: {e}")

    # 9. Subscription Data, Financial Information (Restated), Peer Comparison - Section 8 in your doc
    try:
        # Live Subscription UL (Qualified Institutional Buyers, Non-Institutional Investors, Retail Individual Investor)
        # This is for the UL directly beneath the h2 'AJC Jewel SME IPO Live Subscription' and a div 'biddingDetails'
        live_sub_h2 = soup.find('h2', text=re.compile(r'Live Subscription', re.IGNORECASE))
        if live_sub_h2:
            # Find the ul after the biddingDetails div
            # The structure is h2 -> p -> div#biddingDetails -> div -> ul
            target_div_with_ul = live_sub_h2.find_next_sibling('div', id='biddingDetails').find_next_sibling('div')
            if target_div_with_ul and target_div_with_ul.find('ul'):
                ul_list = target_div_with_ul.find('ul').find_all('li')
                ipo_details['subscription_allocation_percentage_live'] = [get_text_safe(li) for li in ul_list]

        # IPO Bidding Live Updates Table
        bidding_table_caption = soup.find('caption', text=re.compile(r'IPO Bidding Live Updates', re.IGNORECASE))
        if bidding_table_caption:
            bidding_table = bidding_table_caption.find_parent('table')
            if bidding_table:
                bidding_updates = []
                headers = [get_text_safe(th) for th in bidding_table.find('thead').find_all('th')]
                for row in bidding_table.find('tbody').find_all('tr'):
                    row_data = [get_text_safe(td) for td in row.find_all('td')]
                    if len(headers) == len(row_data):
                        bidding_updates.append(dict(zip(headers, row_data)))
                ipo_details['live_bidding_updates_table'] = bidding_updates

        # Financial Information (Restated) Table
        financial_info_h2 = soup.find('h2', text=re.compile(r'Financial Information \(Restated\)', re.IGNORECASE))
        if financial_info_h2:
            # The table is inside a div, inside a div, inside a row -> table-responsive -> table
            financial_table_div = financial_info_h2.find_next_sibling('div')
            if financial_table_div:
                financial_table = financial_table_div.find('table', id='financialTable')
                if financial_table:
                    financial_data = {}
                    rows = financial_table.find('tbody').find_all('tr')
                    if rows:
                        period_headers = [get_text_safe(td) for td in rows[0].find_all('td') if get_text_safe(td)]
                        financial_data['periods'] = period_headers[1:] # Skip "Period Ended" label
                        
                        for row in rows[1:]:
                            cols = row.find_all('td')
                            metric = get_text_safe(cols[0])
                            values = [get_text_safe(td) for td in cols[1:]]
                            financial_data[metric] = values
                    ipo_details['financial_information_restated'] = financial_data

        # Peer Comparison Table
        peer_comparison_h2 = soup.find('h2', text=re.compile(r'Peer Comparison', re.IGNORECASE))
        if peer_comparison_h2:
            peer_table_div = peer_comparison_h2.find_next_sibling('p').find_next_sibling('div') # p then div
            if peer_table_div:
                peer_table = peer_table_div.find('table', class_='table')
                if peer_table:
                    peer_data = []
                    headers = [get_text_safe(th) for th in peer_table.find('thead').find_all('th')]
                    for row in peer_table.find('tbody').find_all('tr'):
                        row_data = [get_text_safe(td) for td in row.find_all('td')]
                        if len(headers) == len(row_data):
                            peer_data.append(dict(zip(headers, row_data)))
                    ipo_details['peer_comparison'] = peer_data

    except Exception as e:
        print(f"  Error extracting Subscription/Financials/Peer Comparison section: {e}")

    # 10. IPO Company data (Company Address, IPO Registrar office, IPO Lead Manager details) - Section 9 in your doc
    try:
        address_cards_row = soup.find('div', class_='row').find_all('div', class_='col-lg-4') # Find all 3 columns
        
        # Company Address (9.1)
        company_address_card = address_cards_row[0] if len(address_cards_row) > 0 else None
        if company_address_card:
            address_body = company_address_card.find('div', class_='card-body')
            if address_body:
                ipo_details['company_address_raw'] = get_text_safe(address_body)
                website_match = re.search(r'Website:\s*(https?://\S+)', ipo_details['company_address_raw'])
                phone_match = re.search(r'Phone:\s*([+\d\s-]+)', ipo_details['company_address_raw'])
                email_match = re.search(r'Email:\s*(\S+@\S+)', ipo_details['company_address_raw'])
                
                if website_match: ipo_details['company_contact_website'] = website_match.group(1).strip()
                if phone_match: ipo_details['company_contact_phone'] = phone_match.group(1).strip()
                if email_match: ipo_details['company_contact_email'] = email_match.group(1).strip()

        # IPO Registrar (9.2)
        registrar_card = address_cards_row[1] if len(address_cards_row) > 1 else None
        if registrar_card:
            registrar_body = registrar_card.find('div', class_='card-body')
            if registrar_body:
                ipo_details['ipo_registrar_raw'] = get_text_safe(registrar_body)
                website_match = re.search(r'Website:\s*(https?://\S+)', ipo_details['ipo_registrar_raw'])
                phone_match = re.search(r'Phone:\s*([+\d\s-]+)', ipo_details['ipo_registrar_raw'])
                email_match = re.search(r'Email:\s*(\S+@\S+)', ipo_details['ipo_registrar_raw'])

                if website_match: ipo_details['ipo_registrar_website'] = website_match.group(1).strip()
                if phone_match: ipo_details['ipo_registrar_phone'] = phone_match.group(1).strip()
                if email_match: ipo_details['ipo_registrar_email'] = email_match.group(1).strip()

        # IPO Lead Manager (9.3)
        lead_manager_card = address_cards_row[2] if len(address_cards_row) > 2 else None
        if lead_manager_card:
            lead_manager_body = lead_manager_card.find('div', class_='card-body')
            if lead_manager_body:
                lead_managers = [get_text_safe(a) for a in lead_manager_body.find_all('a')]
                ipo_details['ipo_lead_managers_html'] = lead_managers # Differentiated from API field

    except Exception as e:
        print(f"  Error extracting Company/Registrar/Lead Manager details: {e}")


    print("[HTML Scraper] HTML parsing complete.")
    return ipo_details


# Example usage for direct testing of this scraper
if __name__ == "__main__":
    # Use the specific URL from your IPO HTML scrap.txt for testing
    target_url = "https://www.investorgain.com/ipo/ajc-jewel-sme-ipo/1281/" 

    html_content = fetch_html_content(target_url)
    if html_content:
        extracted_data = parse_ipo_details_from_html(html_content)
        print("\n--- Extracted IPO Details from HTML ---")
        print(json.dumps(extracted_data, indent=2))
        
        # Save to JSON file for easy review
        with open("scraped_ipo_details_test.json", "w", encoding="utf-8") as f:
            json.dump(extracted_data, f, indent=2, ensure_ascii=False)
        print("\nExtracted data saved to scraped_ipo_details_test.json")

    else:
        print("\nFailed to fetch HTML content. No data to parse.")
