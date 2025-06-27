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

def extract_about_company_section(soup):
    """
    Extracts only the About Company section from the IPO detail page.
    """
    company_data = {}
    
    # Find the About Company section
    about_company_h3 = soup.find('h3', itemprop='about', string=lambda s: s and 'About Company' in s)
    
    if about_company_h3:
        about_company_div = about_company_h3.find_parent('div', class_='col-12')
        if about_company_div:
            
            # 1. Company Description
            description_paragraphs_div = about_company_div.find('div', class_=False, recursive=False)
            if description_paragraphs_div:
                paragraphs = description_paragraphs_div.find_all('p')
                company_data['Company Description'] = " ".join([clean_text(p.get_text(strip=True)) for p in paragraphs])
            else:
                company_data['Company Description'] = 'N/A'

            # 2. Company Strengths
            strengths_h3 = about_company_div.find('h3', string=lambda s: s and 'Strengths' in s)
            if strengths_h3:
                strengths_div = strengths_h3.find_next_sibling('div')
                if strengths_div:
                    strengths_list = [clean_text(li.get_text(strip=True)) for li in strengths_div.find_all('li')]
                    company_data['Company Strengths'] = "; ".join(strengths_list)
                else:
                    company_data['Company Strengths'] = 'N/A'
            else:
                company_data['Company Strengths'] = 'N/A'

            # 3. Company Info Table (Incorporation, Sector, Issue Size, Website)
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
                                company_data[header] = link_tag.get('href') if link_tag else clean_text(cols[i].get_text(strip=True))
                            else:
                                company_data[header] = clean_text(cols[i].get_text(strip=True))
            
            # Fill missing fields with N/A if not found
            expected_fields = ['Incorporation', 'Sector', 'Issue Size', 'Website']
            for field in expected_fields:
                if field not in company_data:
                    company_data[field] = 'N/A'
    else:
        # If About Company section not found, fill with N/A
        company_data = {
            'Company Description': 'N/A',
            'Company Strengths': 'N/A',
            'Incorporation': 'N/A',
            'Sector': 'N/A',
            'Issue Size': 'N/A',
            'Website': 'N/A'
        }
    
    return company_data

def scrape_about_company_data(base_url="https://www.investorgain.com"):
    """
    Main function to scrape only About Company section from IPOs.
    """
    all_company_data = []

    print("Fetching IPO list from API...")
    ipo_list = fetch_ipo_list_from_api()
    if not ipo_list:
        print("No IPOs found or error fetching IPO list. Exiting.")
        return []

    print(f"Found {len(ipo_list)} IPOs via API. Starting About Company scraping...")

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

        print(f"Scraping About Company for: {company_short_name}")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        try:
            response = requests.get(detail_url, headers=headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract only About Company section
            about_company_data = extract_about_company_section(soup)
            
            # Combine basic IPO info with About Company data
            company_info = {
                'IPO ID': ipo_id,
                'Company Name': company_short_name,
                'IPO Category': ipo_category,
                'Detail URL': detail_url,
                **about_company_data  # Merge About Company data
            }
            
            all_company_data.append(company_info)
            print(f"✓ Successfully scraped About Company for {company_short_name}")
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Network error for {company_short_name}: {e}")
        except Exception as e:
            print(f"✗ Parsing error for {company_short_name}: {e}")

        # Be polite with requests
        time.sleep(2)

    return all_company_data

def save_to_csv(data, filename="about_company_data.csv"):
    """
    Saves company data to CSV file.
    """
    if not data:
        print("No data to save.")
        return

    fieldnames = [
        'IPO ID', 'Company Name', 'IPO Category', 'Detail URL',
        'Company Description', 'Company Strengths', 'Incorporation', 
        'Sector', 'Issue Size', 'Website'
    ]

    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                writer.writerow({k: row.get(k, '') for k in fieldnames})
        print(f"✓ Data saved to CSV: {filename}")
    except IOError as e:
        print(f"✗ Error saving CSV: {e}")

def save_to_json(data, filename="about_company_data.json"):
    """
    Saves company data to JSON file.
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"✓ Data saved to JSON: {filename}")
    except IOError as e:
        print(f"✗ Error saving JSON: {e}")

if __name__ == "__main__":
    print("=== IPO About Company Scraper ===")
    
    # Scrape About Company data
    company_data = scrape_about_company_data()
    
    if company_data:
        print(f"\n=== Scraped {len(company_data)} companies ===")
        
        # Save to both formats
        save_to_json(company_data)
        save_to_csv(company_data)
        
        # Display sample data
        print("\n=== Sample Data ===")
        if len(company_data) > 0:
            sample = company_data[0]
            for key, value in sample.items():
                print(f"{key}: {value[:100]}..." if len(str(value)) > 100 else f"{key}: {value}")
    else:
        print("No data was scraped.")
    
    print("\n=== Scraping Complete ===")