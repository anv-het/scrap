import requests
from bs4 import BeautifulSoup
import json
import time
import re
import csv

def fetch_ipo_list_from_api():
    """
    Fetches the list of IPOs from the Investorgain API.
    """
    api_url = "https://webnodejs.investorgain.com/cloud/ipo/list-read"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(api_url, headers=headers, timeout=10) # Added timeout
        response.raise_for_status()  # Raise an exception for HTTP errors
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
        text = re.sub(r'\s+', ' ', text) # Replace multiple spaces with a single space
    return text

def parse_ipo_detail_page(soup):
    """
    Parses the main IPO detail page to extract various sections.
    """
    ipo_details = {}

    # 1. IPO Name
    ipo_name_tag = soup.find('div', class_='col-lg-6')
    if ipo_name_tag:
        h1_tag = ipo_name_tag.find('h1')
        if h1_tag:
            ipo_details['IPO Name'] = clean_text(h1_tag.get_text(strip=True))
    if not ipo_details.get('IPO Name'):
        ipo_details['IPO Name'] = 'N/A'

    # 2. Company Logo
    logo_img_tag = soup.find('div', class_='div-logo')
    if logo_img_tag:
        img_tag = logo_img_tag.find('img')
        if img_tag:
            ipo_details['Company Logo URL'] = img_tag.get('src')
    if not ipo_details.get('Company Logo URL'):
        ipo_details['Company Logo URL'] = 'N/A'


    # 3. IPO Overview Paragraphs
    overview_div = soup.find('div', class_='float-none mb-2 ms-2')
    if overview_div:
        paragraphs = overview_div.find_all('p')
        # For CSV, join paragraphs into a single string
        ipo_details['IPO Overview'] = " ".join([clean_text(p.get_text(strip=True)) for p in paragraphs])
    if not ipo_details.get('IPO Overview'):
        ipo_details['IPO Overview'] = 'N/A'

    # 4. IPO Details Table (e.g., Cedaar Textile SME IPO Details)
    # Find the header, then its sibling table
    ipo_detail_table_header = soup.find('h2', itemprop='about', string=lambda s: s and "SME IPO Details" in s)
    if ipo_detail_table_header:
        detail_table = ipo_detail_table_header.find_next_sibling('table', class_='table table-bordered table-striped table-hover w-auto')
        if detail_table:
            rows = detail_table.find('tbody').find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) == 2:
                    key = clean_text(cols[0].get_text(strip=True)).replace(':', '')
                    value_tag = cols[1]
                    # Check for download links for DRHP/RHP
                    if 'DRHP' in key or 'RHP' in key:
                        link_tag = value_tag.find('a', href=True)
                        if link_tag:
                            ipo_details[key] = link_tag.get('href')
                        else:
                            ipo_details[key] = clean_text(value_tag.get_text(strip=True))
                    else:
                        ipo_details[key] = clean_text(value_tag.get_text(strip=True))

    # 5. Important Dates Table
    dates_table_header = soup.find('h2', itemprop='about', string=lambda s: s and "SME IPO Important Dates" in s)
    if dates_table_header:
        dates_table = dates_table_header.find_next_sibling('table', class_='table table-bordered table-striped table-hover w-auto')
        if dates_table:
            rows = dates_table.find('tbody').find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) == 2:
                    key = clean_text(cols[0].get_text(strip=True)).replace('*', '').replace(':', '')
                    value = clean_text(cols[1].get_text(strip=True))
                    ipo_details[f'Important Date - {key}'] = value # Flatten for CSV/JSON consistency

    # 6. IPO Lots Table
    lots_table_header = soup.find('h2', itemprop='about', string=lambda s: s and "SME IPO Lots" in s)
    if lots_table_header:
        lots_table = lots_table_header.find_next_sibling('table', class_='table table-bordered table-striped table-hover w-auto')
        if lots_table:
            rows = lots_table.find('tbody').find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) == 2:
                    key = clean_text(cols[0].get_text(strip=True)).replace(':', '')
                    value = clean_text(cols[1].get_text(strip=True))
                    ipo_details[f'IPO Lot - {key}'] = value # Flatten for CSV/JSON consistency

    # 7. IPO GMP Table
    gmp_table_header = soup.find('h2', itemprop='about', string=lambda s: s and ('IPO GMP' in s or 'Live GMP' in s))
    if not gmp_table_header: # Fallback if h2 not found
        gmp_table_header = soup.find('h3', itemprop='about', string=lambda s: s and ('IPO GMP' in s or 'Live GMP' in s))

    if gmp_table_header:
        gmp_table = gmp_table_header.find_next_sibling('table', class_='table table-bordered table-striped w-auto')
        if gmp_table:
            headers = [clean_text(th.get_text(strip=True)) for th in gmp_table.find('thead').find_all('th')]
            rows = gmp_table.find('tbody').find_all('tr')
            # For CSV, we'll take the latest GMP (first row) and store as JSON string
            latest_gmp = {}
            if rows:
                cols = rows[0].find_all('td') # Assuming first row is the latest
                for i, col in enumerate(cols):
                    if i < len(headers):
                        latest_gmp[headers[i]] = clean_text(col.get_text(strip=True))
            if latest_gmp:
                ipo_details['Latest GMP Update'] = json.dumps(latest_gmp) # Store as JSON string in CSV cell
            else:
                ipo_details['Latest GMP Update'] = 'N/A'
    if not ipo_details.get('Latest GMP Update'):
        ipo_details['Latest GMP Update'] = 'N/A'

    # 8. About Company Section
    about_company_h3 = soup.find('h3', itemprop='about', string=lambda s: s and 'About Company' in s)
    if about_company_h3:
        about_company_div = about_company_h3.find_parent('div', class_='col-12')
        if about_company_div:
            # Company Description
            description_paragraphs_div = about_company_div.find('div', class_=False, recursive=False)
            if description_paragraphs_div:
                ipo_details['About Company Description'] = " ".join([clean_text(p.get_text(strip=True)) for p in description_paragraphs_div.find_all('p')])

            # Company Strengths
            strengths_h3 = about_company_div.find('h3', string=lambda s: s and 'Strengths' in s)
            if strengths_h3:
                strengths_div = strengths_h3.find_next_sibling('div')
                if strengths_div:
                    ipo_details['Company Strengths'] = "; ".join([clean_text(li.get_text(strip=True)) for li in strengths_div.find_all('li')])

            # Company Info Table (Incorporation, Sector, Issue Size, Website)
            company_info_table = about_company_div.find('table', class_='table table-bordered table-striped table-hover w-auto')
            if company_info_table:
                headers = [clean_text(td.get_text(strip=True)) for td in company_info_table.find('thead').find_all('td')]
                data_row = company_info_table.find('tbody').find('tr')
                if data_row:
                    cols = data_row.find_all('td')
                    for i, header in enumerate(headers):
                        if i < len(cols):
                            if header == 'Website':
                                link_tag = cols[i].find('a', href=True)
                                ipo_details[f'Company Info - {header}'] = link_tag.get('href') if link_tag else clean_text(cols[i].get_text(strip=True))
                            else:
                                ipo_details[f'Company Info - {header}'] = clean_text(cols[i].get_text(strip=True))

    # 9. IPO Objective Section
    objective_h3 = soup.find('h3', itemprop='about', string=lambda s: s and 'Objective' in s)
    if objective_h3:
        # Find the parent of the objective table
        objective_table_div = objective_h3.find_next_sibling('div') # This might be the direct div containing table-responsive
        if objective_table_div:
            objective_table_div = objective_table_div.find('div', class_='table-responsive') # Look for table-responsive within it
        if objective_table_div:
            objective_table = objective_table_div.find('table', id='ObjectiveIssue')
            if objective_table:
                objective_data = []
                rows = objective_table.find('tbody').find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 3: # Assuming S.No., Objects, Amount
                        objective_data.append(f"{clean_text(cols[0].get_text(strip=True))}: {clean_text(cols[1].get_text(strip=True))} ({clean_text(cols[2].get_text(strip=True))} Cr)")
                ipo_details['IPO Objective'] = "; ".join(objective_data)

    # 10. Subscription Data, Financials, and Peer Comparison
    subscription_h2 = soup.find('h2', itemprop='about', string=lambda s: s and 'Live Subscription' in s)
    if subscription_h2:
        parent_div = subscription_h2.find_parent('div', class_='col-12')
        if parent_div:
            # Subscription Share Distribution
            ul_shares = parent_div.find('ul')
            if ul_shares:
                ipo_details['Subscription Share Distribution'] = "; ".join([clean_text(li.get_text(strip=True)) for li in ul_shares.find_all('li')])

            # IPO Bidding Live Updates Table
            # This table might be directly after the subscription H2 or within a div.
            bidding_table = parent_div.find('table', class_='table table-bordered table-striped table-hover w-auto')
            if bidding_table:
                bidding_headers = [clean_text(th.get_text(strip=True)) for th in bidding_table.find('thead').find_all('th')]
                bidding_data_rows = []
                tbody_rows = bidding_table.find('tbody').find_all('tr')
                for row in tbody_rows:
                    row_data_items = []
                    cols = row.find_all('td')
                    for i, col in enumerate(cols):
                        if i < len(bidding_headers):
                            header_text = bidding_headers[i].strip() if bidding_headers[i].strip() else f'Col_{i}'
                            row_data_items.append(f"{header_text}: {clean_text(col.get_text(strip=True))}")
                    if row_data_items:
                        bidding_data_rows.append(" | ".join(row_data_items))
                ipo_details['IPO Bidding Live Updates'] = "; ".join(bidding_data_rows)

    # Financial Information (Restated) Table
    financial_h2 = soup.find('h2', itemprop='about', string=lambda s: s and 'Financial Information (Restated)' in s)
    if financial_h2:
        financial_table_div = financial_h2.find_next_sibling('div', class_='table-responsive')
        if financial_table_div:
            financial_table = financial_table_div.find('table', id='financialTable')
            if financial_table:
                # Extract periods from the second row of tbody (which contains headers for periods)
                period_row = financial_table.find('tbody').find('tr')
                if period_row:
                    period_headers = [clean_text(td.get_text(strip=True)) for td in period_row.find_all('td')]
                    # Now iterate through the rest of the rows for financial metrics
                    financial_data_rows = financial_table.find('tbody').find_all('tr')[1:] # Skip the period headers row itself
                    for row in financial_data_rows:
                        cols = row.find_all('td')
                        if cols:
                            metric_name = clean_text(cols[0].get_text(strip=True)) # First column is the metric name
                            for i, period in enumerate(period_headers[1:], start=1): # Skip the first 'Period Ended' cell
                                if i < len(cols):
                                    ipo_details[f'Financial - {metric_name} ({period})'] = clean_text(cols[i].get_text(strip=True))

    # Peer Comparison Table
    peer_h2 = soup.find('h2', itemprop='about', string=lambda s: s and 'Peer Comparison' in s)
    if peer_h2:
        peer_table_div = peer_h2.find_next_sibling('div', class_='table-responsive')
        if peer_table_div:
            peer_table = peer_table_div.find('table', class_='table table-bordered table-striped table-hover w-auto')
            if peer_table:
                headers = [clean_text(th.get_text(strip=True)) for th in peer_table.find('thead').find_all('th')]
                peer_data_rows = []
                rows = peer_table.find('tbody').find_all('tr')
                for row in rows:
                    entry_data_items = []
                    cols = row.find_all('td')
                    for i, col in enumerate(cols):
                        if i < len(headers):
                            entry_data_items.append(f"{headers[i]}: {clean_text(col.get_text(strip=True))}")
                    if entry_data_items:
                        peer_data_rows.append(" | ".join(entry_data_items))
                ipo_details['Peer Comparison'] = "; ".join(peer_data_rows)

    # 11. Company Address, Registrar, Lead Manager
    # Find the main row containing these cards
    contact_info_row = soup.find('div', class_='row')
    if contact_info_row:
        # Find all columns that might contain these cards
        card_cols = contact_info_row.find_all('div', class_=re.compile(r'col-lg-4|col-md-4|col-sm-4'))
        for col_div in card_cols:
            header = col_div.find('h3')
            if header:
                header_text = clean_text(header.get_text(strip=True))
                card_body = col_div.find('div', class_='card-body')
                if card_body:
                    if 'Company Address' in header_text:
                        company_address_info_text = ""
                        lines = [clean_text(p) for p in card_body.get_text(separator='\n').split('\n') if clean_text(p)]
                        company_address_info_text += f"Name: {clean_text(card_body.find('strong').get_text(strip=True)) if card_body.find('strong') else 'N/A'}; "
                        address_parts = []
                        current_line_idx = 0
                        if card_body.find('strong'):
                            current_line_idx += 1
                        while current_line_idx < len(lines):
                            line = lines[current_line_idx]
                            if 'Website' in line or 'Phone' in line or 'Email' in line:
                                break
                            address_parts.append(line)
                            current_line_idx += 1
                        company_address_info_text += f"Address: {' '.join(address_parts).strip()}; "

                        website_tag = card_body.find('a', href=True)
                        company_address_info_text += f"Website: {website_tag['href'] if website_tag else 'N/A'}; "
                        phone_match = re.search(r'Phone\s*:\s*([+\d\s-]+)', card_body.get_text())
                        company_address_info_text += f"Phone: {phone_match.group(1).strip() if phone_match else 'N/A'}; "
                        email_match = re.search(r'Email\s*:\s*(\S+@\S+)', card_body.get_text())
                        company_address_info_text += f"Email: {email_match.group(1).strip() if email_match else 'N/A'}"
                        ipo_details['Company Address'] = company_address_info_text

                    elif 'Registrar' in header_text:
                        registrar_info_text = ""
                        lines = [clean_text(p) for p in card_body.get_text(separator='\n').split('\n') if clean_text(p)]
                        registrar_info_text += f"Name: {clean_text(card_body.find('strong').get_text(strip=True)) if card_body.find('strong') else 'N/A'}; "
                        address_parts = []
                        current_line_idx = 0
                        if card_body.find('strong'):
                            current_line_idx += 1
                        while current_line_idx < len(lines):
                            line = lines[current_line_idx]
                            if 'Website' in line or 'Phone' in line or 'Email' in line:
                                break
                            address_parts.append(line)
                            current_line_idx += 1
                        registrar_info_text += f"Address: {' '.join(address_parts).strip()}; "

                        website_tag = card_body.find('a', href=True)
                        registrar_info_text += f"Website: {website_tag['href'] if website_tag else 'N/A'}; "
                        phone_match = re.search(r'Phone\s*:\s*([+\d\s-]+)', card_body.get_text())
                        registrar_info_text += f"Phone: {phone_match.group(1).strip() if phone_match else 'N/A'}; "
                        email_match = re.search(r'Email\s*:\s*(\S+@\S+)', card_body.get_text())
                        registrar_info_text += f"Email: {email_match.group(1).strip() if email_match else 'N/A'}"
                        ipo_details['IPO Registrar'] = registrar_info_text

                    elif 'Lead Manager' in header_text:
                        lead_managers_text = []
                        li_tags = card_body.find_all('li')
                        for li in li_tags:
                            link = li.find('a', href=True)
                            if link:
                                lead_managers_text.append(f"{clean_text(link.get_text(strip=True))} ({link.get('href')})")
                            else:
                                lead_managers_text.append(clean_text(li.get_text(strip=True)))
                        ipo_details['IPO Lead Manager(s)'] = "; ".join(lead_managers_text)

    return ipo_details


def scrape_investorgain_ipo_details(base_url="https://www.investorgain.com"):
    """
    Main function to orchestrate the scraping process.
    """
    all_ipo_data = []

    print("Fetching IPO list from API...")
    ipo_list = fetch_ipo_list_from_api()
    if not ipo_list:
        print("No IPOs found or error fetching IPO list. Exiting.")
        return []

    print(f"Found {len(ipo_list)} IPOs via API. Starting detailed scraping...")

    # Iterate through all IPOs found from the API
    for i, ipo_entry in enumerate(ipo_list):
        company_short_name = ipo_entry.get('company_short_name')
        url_rewrite_folder_name = ipo_entry.get('urlrewrite_folder_name')
        ipo_category = ipo_entry.get('ipo_category')
        ipo_id = ipo_entry.get('id')

        if not url_rewrite_folder_name or not ipo_id:
            print(f"Skipping {company_short_name} due to missing URL folder name or ID.")
            continue

        # Construct the detail page URL
        detail_url = f"{base_url}/ipo/{url_rewrite_folder_name}/{ipo_id}/"

        print(f"\nScraping details for {company_short_name} ({ipo_category} IPO) from: {detail_url}")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        try:
            response = requests.get(detail_url, headers=headers, timeout=15) # Added timeout
            response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
            soup = BeautifulSoup(response.content, 'html.parser')
            detailed_data = parse_ipo_detail_page(soup)
            # Merge API data with scraped data. Scraped data will override if keys overlap.
            merged_data = {**ipo_entry, **detailed_data}
            all_ipo_data.append(merged_data)
            print(f"Successfully scraped {company_short_name}.")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching detail page for {company_short_name} ({detail_url}): {e}")
        except Exception as e:
            print(f"Error parsing detail page for {company_short_name}: {e}")

        time.sleep(2) # Be polite and wait for 2 seconds before next request

    return all_ipo_data

def save_to_csv(data, filename="ipo_details.csv"):
    """
    Saves a list of dictionaries to a CSV file.
    It automatically determines headers and flattens data for CSV compatibility.
    """
    if not data:
        print("No data to save to CSV.")
        return

    # Determine all unique fieldnames (headers)
    fieldnames = set()
    for row in data:
        fieldnames.update(row.keys())

    # Sort fieldnames for consistent column order (optional but good practice)
    fieldnames = sorted(list(fieldnames))

    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader() # Write the column headers
            for row in data:
                # Ensure all fields are present for DictWriter, fill missing with empty string
                # This handles cases where some IPOs might not have data for all columns
                writer.writerow({k: row.get(k, '') for k in fieldnames})
        print(f"Data successfully saved to CSV: {filename}")
    except IOError as e:
        print(f"Error saving to CSV file: {e}")

if __name__ == "__main__":
    scraped_data = scrape_investorgain_ipo_details()
    if scraped_data:
        # Save to JSON file
        json_filename = "ipo_details.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(scraped_data, f, ensure_ascii=False, indent=4)
        print(f"\nAll IPO data saved to '{json_filename}'")

        # Save to CSV file
        csv_filename = "ipo_details.csv"
        save_to_csv(scraped_data, csv_filename)
    else:
        print("No data was scraped to save.")