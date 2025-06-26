import requests
from bs4 import BeautifulSoup
import json
import re
import os # Import os module for file path operations

# Base URLs for API and detail pages
IPO_LIST_API = 'https://webnodejs.investorgain.com/cloud/ipo/list-read'
IPO_DETAIL_BASE_URL = 'https://www.investorgain.com/ipo/'
OUTPUT_FILE_NAME_JSON = 'ipo_data_v2.json' # Original JSON output
OUTPUT_FILE_NAME_TXT = 'ipo_data_summary.txt' # New text output

def fetch_html_content(url):
    """
    Fetches HTML content from a given URL.
    Args:
        url (str): The URL to fetch.
    Returns:
        str: The HTML content as a string, or None if an error occurs.
    """
    try:
        response = requests.get(url, timeout=15) # Increased timeout
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None

def extract_table_data(table_element):
    """
    Extracts key-value pairs from a given BeautifulSoup table element.
    It attempts to find a header cell (th or first td) and a value cell (last td).
    Args:
        table_element (BeautifulSoup tag): The HTML table element to extract data from.
    Returns:
        dict: A dictionary containing the extracted data.
    """
    data = {}
    if not table_element: # Add check for None table_element
        return data

    rows = table_element.find_all('tr')
    for row in rows:
        header_cell = row.find('th') or row.find('td') # Prioritize th, then first td

        value_cell = None
        # Try to find td with data-title first, then the last td
        data_title_td = row.find('td', {'data-title': True})
        if data_title_td:
            value_cell = data_title_td
        else:
            all_tds = row.find_all('td')
            if all_tds:
                if len(all_tds) > 1:
                    value_cell = all_tds[1] # Assume value is often the second cell in standard rows
                elif len(all_tds) == 1:
                    # If only one td, it could be both header and value in a simple structure
                    # Or it's a malformed row, or a header row only.
                    # For now, let's keep it as is, and the header_cell == value_cell check might help.
                    pass
                
                # Refined logic: If header_cell and value_cell initially point to the same td
                # and there's more than one td, try the last td as the value.
                if header_cell and value_cell and header_cell == value_cell and len(all_tds) > 1:
                    value_cell = all_tds[-1]


        if header_cell and value_cell:
            key_text = header_cell.get_text(strip=True).replace(':', '').replace('*', '').strip()
            # Remove content in parentheses for keys
            key = re.sub(r'\s*\(.*?\)\s*', '', key_text).strip()

            value_element = value_cell.find('a')
            if value_element and 'href' in value_element.attrs:
                value = value_element['href'].strip()
            else:
                value = value_cell.get_text(strip=True).strip()

            if key and value: # Ensure both key and value are non-empty
                data[key] = value
    return data

def extract_paragraph_content(parent_element):
    """
    Extracts text content from a block of paragraphs.
    Args:
        parent_element (BeautifulSoup tag): The parent element containing the paragraphs.
    Returns:
        str: The concatenated text content.
    """
    if not parent_element:
        return None
    paragraphs = parent_element.find_all('p')
    content = '\n\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
    return content if content else None

def extract_list_content(parent_element):
    """
    Extracts text content from a block of list items.
    Args:
        parent_element (BeautifulSoup tag): The parent element containing the list items.
    Returns:
        list: A list of strings, each representing a list item.
    """
    if not parent_element:
        return []
    list_items = parent_element.find_all('li')
    content_list = [li.get_text(strip=True) for li in list_items if li.get_text(strip=True)]
    return content_list if content_list else []

def extract_table_by_heading(soup, heading_texts):
    """
    Extracts data from a specific table identified by its heading text.
    Searches for h2/h3 tags containing the heading text and then finds the next sibling table.
    Args:
        soup (BeautifulSoup object): The HTML document.
        heading_texts (list or str): A string or list of strings of the heading text(s) (h2 or h3)
                                     preceding the table.
    Returns:
        dict or None: The extracted table data, or None if not found.
    """
    if isinstance(heading_texts, str):
        heading_texts = [heading_texts]

    for h_text in heading_texts:
        # Using a regex for broader matching, e.g., 'IPO Important Dates' will match 'Cedaar Textile SME IPO Important Dates'
        heading_tag = soup.find(['h2', 'h3'], string=re.compile(re.escape(h_text.strip()), re.IGNORECASE))
        if heading_tag:
            current_element = heading_tag.find_next_sibling()
            while current_element:
                if current_element.name == 'table':
                    return extract_table_data(current_element)
                # If it's a div containing a table, look inside
                if current_element.name == 'div' and current_element.find('table'):
                    return extract_table_data(current_element.find('table'))
                current_element = current_element.find_next_sibling()
    return None

def extract_ipo_data(html_content):
    """
    Extracts all specified data points from a single IPO detail page HTML content.
    Tracks which data points were found and which were missed.
    Args:
        html_content (str): The HTML content of an IPO detail page.
    Returns:
        tuple: A tuple containing (dict of extracted IPO data, dict of missing data keys).
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    ipo_data = {}
    missing_data = {}

    # Helper function to assign data and track missing
    def assign_data(key, extractor_func, *args, **kwargs):
        data = extractor_func(*args, **kwargs)
        if data:
            ipo_data[key] = data
        else:
            ipo_data[key] = None # Explicitly set to None for consistent output
            missing_data[key] = "Not Found"
        return data # Return extracted data for immediate use if needed

    # 1. IPO name
    ipo_name_tag = soup.select_one('div.col-lg-6 h1')
    if ipo_name_tag:
        ipo_name = ipo_name_tag.get_text(strip=True).replace('\xa0', ' ')
        # Remove common trailing text from the IPO name
        # Make the regex more flexible for variations
        ipo_name = re.sub(r'(IPO|SME IPO) (Details \d{4}|Important Dates).*', '', ipo_name, flags=re.IGNORECASE).strip()
        ipo_data['IPO Name'] = ipo_name if ipo_name else None
        if not ipo_name: missing_data['IPO Name'] = "Not Found"
    else:
        ipo_data['IPO Name'] = None
        missing_data['IPO Name'] = "Not Found (h1 tag not found)"


    # 2. Company Logo URL
    company_logo_tag = soup.select_one('.div-logo img')
    assign_data('Company Logo URL', lambda: company_logo_tag['src'] if company_logo_tag and 'src' in company_logo_tag.attrs else None)

    # 3. Description paragraphs
    description_div = soup.select_one('div.float-none.mb-2.ms-2')
    assign_data('Company Description', extract_paragraph_content, description_div)

    # 4. IPO SME IPO Details Table
    ipo_details_h2 = soup.find('h2', itemprop="about", string=re.compile(r'(.*IPO Details|.*SME IPO Details)', re.IGNORECASE))
    if ipo_details_h2:
        ipo_details_table = ipo_details_h2.find_next_sibling('table', class_='table')
        if not ipo_details_table: # Also check if table is wrapped in a div.table-responsive
            div_wrapper = ipo_details_h2.find_next_sibling('div', class_='table-responsive')
            if div_wrapper:
                ipo_details_table = div_wrapper.find('table', class_='table')
        assign_data('IPO Details', extract_table_data, ipo_details_table)
    else:
        ipo_data['IPO Details'] = None
        missing_data['IPO Details'] = "Not Found (h2 heading for IPO Details missing)"


    # 5. IPO Important Dates Table
    assign_data('Important Dates', extract_table_by_heading, soup, ['IPO Important Dates', 'SME IPO Important Dates'])

    # 6. IPO Lots Table
    assign_data('IPO Lots', extract_table_by_heading, soup, ['IPO Lots', 'SME IPO Lots'])

    # 7. IPO GMP Table
    # Re-evaluate GMP extraction - the provided JSON shows an issue
    gmp_table = extract_table_by_heading(soup, ['IPO GMP**', 'IPO Grey Market Premium (GMP)', 'SME IPO Grey Market Premium (GMP)'])
    if gmp_table:
        # Assuming GMP table structure is simple key-value, but the example JSON shows a date as value.
        # If the table has specific columns for GMP, Kostak, etc., need to adapt extract_table_data
        # For now, just assign the extracted table data as is.
        ipo_data['IPO GMP'] = gmp_table
    else:
        ipo_data['IPO GMP'] = None
        missing_data['IPO GMP'] = "Not Found (GMP heading/table missing)"


    # 8. About Company and Strengths
    about_company_h3 = soup.find('h3', itemprop="about", string=re.compile(r'About Company - .*', re.IGNORECASE))
    if about_company_h3:
        about_company_div = about_company_h3.find_next_sibling('div')
        if about_company_div:
            content_source = about_company_div.find('div', class_='text-start') or about_company_div
            assign_data('About Company', extract_paragraph_content, content_source)
        else:
            ipo_data['About Company'] = None
            missing_data['About Company'] = "Not Found (content div after About Company heading missing)"
    else:
        ipo_data['About Company'] = None
        missing_data['About Company'] = "Not Found (About Company heading missing)"

    strengths_h3 = soup.find('h3', string=re.compile(r'.*IPO Strengths', re.IGNORECASE))
    if strengths_h3:
        strengths_container = strengths_h3.find_next_sibling('div')
        if strengths_container:
            assign_data('Strengths', extract_list_content, strengths_container.find('ul'))
        else:
            ipo_data['Strengths'] = None
            missing_data['Strengths'] = "Not Found (container for strengths list missing)"
    else:
        ipo_data['Strengths'] = None
        missing_data['Strengths'] = "Not Found (Strengths heading missing)"


    # 9. Company Info Table (Incorporation, Sector, etc.)
    company_info_table_container = soup.find('div', class_='table-responsive')
    if company_info_table_container:
        company_info_table = company_info_table_container.find('table', class_='table-bordered')
        if company_info_table:
            headers = [th.get_text(strip=True) for th in company_info_table.select('thead tr td')]
            values_row = company_info_table.select_one('tbody tr')
            
            extracted_company_info = {}
            if values_row and headers:
                values = [td.get_text(strip=True) for td in values_row.find_all('td')]

                # Special handling for Website link
                website_td = values_row.find('a', title=re.compile(r'.*Website'))
                if website_td and 'href' in website_td.attrs:
                    try:
                        website_index = headers.index('Website')
                        if website_index < len(values):
                            values[website_index] = website_td['href']
                        else:
                            # If 'Website' header exists but no corresponding value td, extend values
                            values.extend([None] * (website_index - len(values) + 1))
                            values[website_index] = website_td['href']
                    except ValueError:
                        pass # 'Website' header not found, proceed without special handling

                if len(values) < len(headers):
                    values.extend([None] * (len(headers) - len(values)))
                
                extracted_company_info = dict(zip(headers, values))
            assign_data('Company General Info', lambda: extracted_company_info if extracted_company_info else None)
        else:
            ipo_data['Company General Info'] = None
            missing_data['Company General Info'] = "Not Found (table-bordered inside table-responsive missing)"
    else:
        ipo_data['Company General Info'] = None
        missing_data['Company General Info'] = "Not Found (table-responsive container missing)"


    # 10. IPO Objective Data
    objectives_list = []
    objective_table_h3 = soup.find('h3', string=re.compile(r'.*IPO Objective', re.IGNORECASE))
    if objective_table_h3:
        objective_container = objective_table_h3.find_next_sibling('div')
        if objective_container:
            objective_table = objective_container.find('table')
            if objective_table:
                for row in objective_table.select('tbody tr'):
                    cols = row.find_all('td')
                    if len(cols) >= 3:
                        objectives_list.append({
                            'S.No.': cols[0].get_text(strip=True),
                            'Objects of the Issue': cols[1].get_text(strip=True),
                            'Expected Amount (Rs. in crores)': cols[2].get_text(strip=True)
                        })
    assign_data('IPO Objective', lambda: objectives_list if objectives_list else None)


    # 11. Subscription data
    subscription_h2 = soup.find('h2', itemprop="about", string=re.compile(r'.*Live Subscription.*', re.IGNORECASE))
    if subscription_h2:
        # Extract bullet points (Overview)
        subscription_ul_parent = subscription_h2.find_next_sibling('div')
        assign_data('Subscription Overview', extract_list_content, subscription_ul_parent.find('ul') if subscription_ul_parent else None)

        # Extract subscription table (Live Updates)
        subscription_table_caption = soup.find('caption', string=re.compile(r'IPO Bidding Live Updates.*', re.IGNORECASE))
        if subscription_table_caption:
            subscription_table = subscription_table_caption.find_parent('table')
            if subscription_table:
                headers = [th.get_text(strip=True) for th in subscription_table.select('thead tr th') if th.get_text(strip=True)]
                table_rows = []
                for row in subscription_table.select('tbody tr'):
                    row_data = {}
                    cols = row.find_all('td')
                    if cols:
                        for i, col in enumerate(cols):
                            data_title = col.get('data-title')
                            if data_title:
                                row_data[data_title.replace('-', ' ').strip()] = col.get_text(strip=True)
                            elif i < len(headers):
                                row_data[headers[i]] = col.get_text(strip=True)
                        table_rows.append(row_data)
                assign_data('IPO Bidding Live Updates', lambda: table_rows if table_rows else None)
            else:
                ipo_data['IPO Bidding Live Updates'] = None
                missing_data['IPO Bidding Live Updates'] = "Not Found (Subscription table missing under caption)"
        else:
            ipo_data['IPO Bidding Live Updates'] = None
            missing_data['IPO Bidding Live Updates'] = "Not Found (Subscription table caption missing)"
    else:
        ipo_data['Subscription Overview'] = None
        ipo_data['IPO Bidding Live Updates'] = None
        missing_data['Subscription Overview'] = "Not Found (Live Subscription heading missing)"
        missing_data['IPO Bidding Live Updates'] = "Not Found (Live Subscription heading missing)"


    # 12. IPO Financial Information (Restated Consolidated)
    assign_data('Financial Information', extract_table_by_heading, soup, ['Financial Information (Restated)', 'Financial Information (Restated Consolidated)'])

    # 13. Ipo IPO Peer Comparison Data
    assign_data('Peer Comparison', extract_table_by_heading, soup, 'Peer Comparison')

    # 14. Company Address, IPO Registrar, IPO Lead Manager
    company_address_card_h3 = soup.find('h3', string=re.compile(r'Company Address', re.IGNORECASE))
    if company_address_card_h3:
        parent_card_body = company_address_card_h3.find_parent('div', class_='card').find('div', class_='card-body')
        if parent_card_body:
            contact_info_raw = parent_card_body.get_text(separator='\n', strip=True)
            
            # Use a list to build up address parts
            address_parts = []
            # Filter out lines that are purely for contact info from the address
            for content_node in parent_card_body.children:
                if isinstance(content_node, str) and content_node.strip():
                    part = content_node.strip()
                    if not any(keyword in part for keyword in ['Website:', 'Phone:', 'Email:']):
                        address_parts.append(part)
                elif content_node.name in ['strong', 'div'] and content_node.get_text(strip=True):
                    part = content_node.get_text(strip=True)
                    if not any(keyword in part for keyword in ['Website:', 'Phone:', 'Email:']):
                        address_parts.append(part)

            extracted_address = '\n'.join(address_parts).strip()
            assign_data('Company Address', lambda: extracted_address if extracted_address else None)

            website_match = re.search(r'Website:\s*(https?://\S+)', contact_info_raw)
            assign_data('Company Website', lambda: website_match.group(1).strip() if website_match else None)

            phone_match = re.search(r'Phone:\s*([+\d\s-]+)', contact_info_raw)
            assign_data('Company Phone', lambda: phone_match.group(1).strip() if phone_match else None)

            email_match = re.search(r'Email:\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', contact_info_raw)
            assign_data('Company Email', lambda: email_match.group(1).strip() if email_match else None)
        else:
            ipo_data['Company Address'] = None
            ipo_data['Company Website'] = None
            ipo_data['Company Phone'] = None
            ipo_data['Company Email'] = None
            missing_data['Company Address'] = "Not Found (card-body for address missing)"
            missing_data['Company Website'] = "Not Found (card-body for address missing)"
            missing_data['Company Phone'] = "Not Found (card-body for address missing)"
            missing_data['Company Email'] = "Not Found (card-body for address missing)"
    else:
        ipo_data['Company Address'] = None
        ipo_data['Company Website'] = None
        ipo_data['Company Phone'] = None
        ipo_data['Company Email'] = None
        missing_data['Company Address'] = "Not Found (Company Address heading missing)"
        missing_data['Company Website'] = "Not Found (Company Address heading missing)"
        missing_data['Company Phone'] = "Not Found (Company Address heading missing)"
        missing_data['Company Email'] = "Not Found (Company Address heading missing)"


    registrar_card_h3 = soup.find('h3', string=re.compile(r'.*IPO Registrar', re.IGNORECASE))
    if registrar_card_h3:
        parent_card_body = registrar_card_h3.find_parent('div', class_='card').find('div', class_='card-body')
        assign_data('IPO Registrar', lambda: parent_card_body.get_text(separator='\n', strip=True) if parent_card_body else None)
    else:
        ipo_data['IPO Registrar'] = None
        missing_data['IPO Registrar'] = "Not Found (IPO Registrar heading missing)"

    lead_manager_card_h3 = soup.find('h3', string=re.compile(r'.*IPO Lead Manager', re.IGNORECASE))
    if lead_manager_card_h3:
        parent_card_body = lead_manager_card_h3.find_parent('div', class_='card').find('div', class_='card-body')
        if parent_card_body:
            lead_managers = [a.get_text(strip=True) for a in parent_card_body.find_all('a') if a.get_text(strip=True)]
            assign_data('IPO Lead Manager', lambda: lead_managers if lead_managers else None)
        else:
            ipo_data['IPO Lead Manager'] = None
            missing_data['IPO Lead Manager'] = "Not Found (card-body for lead manager missing)"
    else:
        ipo_data['IPO Lead Manager'] = None
        missing_data['IPO Lead Manager'] = "Not Found (IPO Lead Manager heading missing)"

    # 15. Last Updated Timestamp
    last_updated_div = soup.find('div', class_='float-end.my-2')
    if last_updated_div:
        last_updated_text = last_updated_div.get_text(strip=True)
        assign_data('Last Updated', lambda: last_updated_text.replace('Last Updated on ', '').strip() if 'Last Updated on' in last_updated_text else last_updated_text)
    else:
        ipo_data['Last Updated'] = None
        missing_data['Last Updated'] = "Not Found (Last Updated div missing)"
    
    return ipo_data, missing_data

def main():
    """
    Main function to orchestrate the scraping process and save data to JSON and a text file.
    """
    all_ipo_data = []
    summary_output_lines = []

    print("Fetching IPO list...")
    list_api_response = fetch_html_content(IPO_LIST_API)
    if not list_api_response:
        print("Failed to fetch IPO list API. Exiting.")
        return

    try:
        ipo_list_json = json.loads(list_api_response)
        if ipo_list_json.get('msg') == 1 and ipo_list_json.get('ipoList'):
            ipo_companies = ipo_list_json['ipoList']
            print(f"Found {len(ipo_companies)} IPOs. Starting detail scraping...")
            summary_output_lines.append(f"Total IPOs found: {len(ipo_companies)}\n")

            for ipo_info in ipo_companies:
                company_folder_name = ipo_info.get('urlrewrite_folder_name')
                ipo_id = ipo_info.get('id')
                company_short_name = ipo_info.get('company_short_name', 'Unknown IPO')

                summary_output_lines.append(f"\n--- Processing IPO: {company_short_name} (ID: {ipo_id}) ---")

                if company_folder_name and ipo_id:
                    detail_url = f"{IPO_DETAIL_BASE_URL}{company_folder_name}/{ipo_id}/"
                    print(f"Scraping details for '{company_short_name}' from: {detail_url}")
                    summary_output_lines.append(f"  Detail URL: {detail_url}")
                    detail_html = fetch_html_content(detail_url)

                    if detail_html:
                        extracted_data, missing_data = extract_ipo_data(detail_html)
                        if extracted_data:
                            # Merge basic IPO info from API with detailed scraped data
                            merged_data = {**ipo_info, **extracted_data}
                            all_ipo_data.append(merged_data)
                            print(f"Successfully scraped data for '{company_short_name}'.")
                            summary_output_lines.append(f"  Status: Successfully Scraped.")
                            
                            # Add a section for extracted data
                            summary_output_lines.append(f"  Extracted Data Points:")
                            for key, value in merged_data.items():
                                if key not in missing_data and key not in ipo_info: # Only show newly extracted or critical ones
                                    summary_output_lines.append(f"    - {key}: Present (Length: {len(value) if isinstance(value, (list, dict, str)) else 'N/A'})")

                            # Add a section for missing data
                            if missing_data:
                                summary_output_lines.append(f"  Missing Data Points:")
                                for key, reason in missing_data.items():
                                    summary_output_lines.append(f"    - {key}: {reason}")
                            else:
                                summary_output_lines.append(f"  All expected data points were found for this IPO.")
                        else:
                            print(f"Could not extract detailed data for '{company_short_name}' from {detail_url}.")
                            summary_output_lines.append(f"  Status: Failed to extract detailed data.")
                            summary_output_lines.append(f"  Missing Data (likely all): {missing_data}")
                    else:
                        print(f"Failed to fetch detail HTML for '{company_short_name}'. Skipping.")
                        summary_output_lines.append(f"  Status: Failed to fetch detail HTML.")
                else:
                    print(f"Skipping IPO due to missing folder name or ID: {ipo_info.get('company_short_name', 'N/A')} (ID: {ipo_info.get('id', 'N/A')}).")
                    summary_output_lines.append(f"  Status: Skipped (missing folder name or ID).")
        else:
            print("IPO list API response format unexpected or ipoList is empty.")
            summary_output_lines.append("IPO list API response format unexpected or ipoList is empty.")

    except json.JSONDecodeError as e:
        print(f"Error decoding IPO list API JSON: {e}")
        summary_output_lines.append(f"Error decoding IPO list API JSON: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during processing an IPO: {e}")
        summary_output_lines.append(f"An unexpected error occurred: {e}")

    # Save the results to a JSON file
    if all_ipo_data:
        try:
            with open(OUTPUT_FILE_NAME_JSON, 'w', encoding='utf-8') as f:
                json.dump(all_ipo_data, f, indent=2, ensure_ascii=False)
            print(f"\nScraping finished. Total IPOs scraped: {len(all_ipo_data)}")
            print(f"Data saved to '{OUTPUT_FILE_NAME_JSON}' in the same directory.")
            summary_output_lines.append(f"\nScraping finished. Total IPOs scraped: {len(all_ipo_data)}")
            summary_output_lines.append(f"Raw JSON data saved to '{OUTPUT_FILE_NAME_JSON}'.")
        except IOError as e:
            print(f"Error saving JSON data to file '{OUTPUT_FILE_NAME_JSON}': {e}")
            summary_output_lines.append(f"Error saving JSON data to file '{OUTPUT_FILE_NAME_JSON}': {e}")
    else:
        print("\nNo IPO data was successfully scraped and nothing saved to JSON file.")
        summary_output_lines.append("\nNo IPO data was successfully scraped and nothing saved to JSON file.")

    # Save the summary to a text file
    try:
        with open(OUTPUT_FILE_NAME_TXT, 'w', encoding='utf-8') as f:
            f.write('\n'.join(summary_output_lines))
        print(f"Summary of scraping process saved to '{OUTPUT_FILE_NAME_TXT}'.")
    except IOError as e:
        print(f"Error saving summary to text file '{OUTPUT_FILE_NAME_TXT}': {e}")

if __name__ == "__main__":
    main()