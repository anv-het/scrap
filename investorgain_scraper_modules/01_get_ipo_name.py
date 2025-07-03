import requests
from bs4 import BeautifulSoup
import json
import time
import re
import csv
import os
from urllib.parse import urljoin

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

def extract_company_name_and_logo(soup, base_url):
    """
    Extracts only the Company Name and Company Logo from the IPO detail page.
    """
    company_data = {}
    
    # 1. Extract IPO/Company Name
    ipo_name_tag = soup.find('div', class_='col-lg-6')
    if ipo_name_tag:
        h1_tag = ipo_name_tag.find('h1')
        if h1_tag:
            company_data['Company Name'] = clean_text(h1_tag.get_text(strip=True))
    
    # If not found in h1, try alternative selectors
    if not company_data.get('Company Name'):
        # Try other possible selectors for company name
        title_tag = soup.find('title')
        if title_tag:
            title_text = title_tag.get_text(strip=True)
            # Extract company name from title (usually in format "Company Name IPO...")
            if 'IPO' in title_text:
                company_name = title_text.split('IPO')[0].strip()
                company_data['Company Name'] = clean_text(company_name)
    
    # Fallback to N/A if still not found
    if not company_data.get('Company Name'):
        company_data['Company Name'] = 'N/A'

    # 2. Extract Company Logo
    logo_img_tag = soup.find('div', class_='div-logo')
    if logo_img_tag:
        img_tag = logo_img_tag.find('img')
        if img_tag:
            logo_src = img_tag.get('src')
            # Convert relative URLs to absolute URLs
            if logo_src:
                if logo_src.startswith('http'):
                    company_data['Company Logo URL'] = logo_src
                else:
                    company_data['Company Logo URL'] = urljoin(base_url, logo_src)
            else:
                company_data['Company Logo URL'] = 'N/A'
        else:
            company_data['Company Logo URL'] = 'N/A'
    else:
        company_data['Company Logo URL'] = 'N/A'
    
    return company_data

def download_logo(logo_url, company_name, logos_folder="company_logos"):
    """
    Downloads the company logo and saves it locally.
    Returns the local file path if successful, None otherwise.
    """
    if logo_url == 'N/A' or not logo_url:
        return None
    
    try:
        # Create logos folder if it doesn't exist
        if not os.path.exists(logos_folder):
            os.makedirs(logos_folder)
        
        # Clean company name for filename
        safe_company_name = re.sub(r'[<>:"/\\|?*]', '_', company_name)
        safe_company_name = safe_company_name.replace(' ', '_')
        
        # Get file extension from URL
        file_extension = logo_url.split('.')[-1].split('?')[0]  # Remove query parameters
        if file_extension.lower() not in ['jpg', 'jpeg', 'png', 'gif', 'svg', 'webp']:
            file_extension = 'jpg'  # Default extension
        
        filename = f"{safe_company_name}_logo.{file_extension}"
        filepath = os.path.join(logos_folder, filename)
        
        # Download the logo
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(logo_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Save the file
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        print(f"    ✓ Logo downloaded: {filename}")
        return filepath
        
    except Exception as e:
        print(f"    ✗ Error downloading logo for {company_name}: {e}")
        return None

def scrape_company_names_and_logos(base_url="https://www.investorgain.com", download_logos=False):
    """
    Main function to scrape only Company Names and Logos from IPOs.
    """
    all_company_data = []

    print("Fetching IPO list from API...")
    ipo_list = fetch_ipo_list_from_api()
    if not ipo_list:
        print("No IPOs found or error fetching IPO list. Exiting.")
        return []

    print(f"Found {len(ipo_list)} IPOs via API. Starting Company Name & Logo scraping...")

    for i, ipo_entry in enumerate(ipo_list, 1):
        company_short_name = ipo_entry.get('company_short_name')
        url_rewrite_folder_name = ipo_entry.get('urlrewrite_folder_name')
        ipo_category = ipo_entry.get('ipo_category')
        ipo_id = ipo_entry.get('id')

        if not url_rewrite_folder_name or not ipo_id:
            print(f"[{i}/{len(ipo_list)}] Skipping {company_short_name} - missing URL data")
            continue

        # Construct the detail page URL
        detail_url = f"{base_url}/ipo/{url_rewrite_folder_name}/{ipo_id}/"

        print(f"[{i}/{len(ipo_list)}] Scraping: {company_short_name}")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        try:
            response = requests.get(detail_url, headers=headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract Company Name and Logo
            name_logo_data = extract_company_name_and_logo(soup, base_url)
            
            # Combine basic IPO info with extracted data
            company_info = {
                'IPO ID': ipo_id,
                'API Company Name': company_short_name,  # Name from API
                'Scraped Company Name': name_logo_data['Company Name'],  # Name from webpage
                'IPO Category': ipo_category,
                'Detail URL': detail_url,
                'Company Logo URL': name_logo_data['Company Logo URL']
            }
            
            # Download logo if requested
            local_logo_path = None
            if download_logos and name_logo_data['Company Logo URL'] != 'N/A':
                local_logo_path = download_logo(
                    name_logo_data['Company Logo URL'], 
                    name_logo_data['Company Name']
                )
            
            company_info['Local Logo Path'] = local_logo_path if local_logo_path else 'N/A'
            
            all_company_data.append(company_info)
            print(f"    ✓ Success - Logo: {'Found' if name_logo_data['Company Logo URL'] != 'N/A' else 'Not Found'}")
            
        except requests.exceptions.RequestException as e:
            print(f"    ✗ Network error: {e}")
        except Exception as e:
            print(f"    ✗ Parsing error: {e}")

        # Be polite with requests
        time.sleep(1.5)

    return all_company_data

# def save_to_csv(data, filename="company_names_logos.csv"):
#     """
#     Saves company data to CSV file.
#     """
#     if not data:
#         print("No data to save.")
#         return

#     fieldnames = [
#         'IPO ID', 'API Company Name', 'Scraped Company Name', 'IPO Category',
#         'Detail URL', 'Company Logo URL', 'Local Logo Path'
#     ]

#     try:
#         with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
#             writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#             writer.writeheader()
#             for row in data:
#                 writer.writerow({k: row.get(k, '') for k in fieldnames})
#         print(f"✓ Data saved to CSV: {filename}")
#     except IOError as e:
#         print(f"✗ Error saving CSV: {e}")

def save_to_json(data, filename="01_company_names_logos.json"):
    """
    Saves company data to JSON file.
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"✓ Data saved to JSON: {filename}")
    except IOError as e:
        print(f"✗ Error saving JSON: {e}")

def print_summary(data):
    """
    Prints a summary of the scraped data.
    """
    if not data:
        return
    
    total_companies = len(data)
    companies_with_logos = len([d for d in data if d.get('Company Logo URL') != 'N/A'])
    companies_with_downloaded_logos = len([d for d in data if d.get('Local Logo Path') != 'N/A'])
    
    print(f"\n=== SCRAPING SUMMARY ===")
    print(f"Total Companies Scraped: {total_companies}")
    print(f"Companies with Logo URLs: {companies_with_logos}")
    print(f"Companies with Downloaded Logos: {companies_with_downloaded_logos}")
    print(f"Success Rate: {(companies_with_logos/total_companies)*100:.1f}%")

if __name__ == "__main__":
    print("=== IPO Company Name & Logo Scraper ===")
    
    # Ask user if they want to download logos
    download_choice = input("Do you want to download logos locally? (y/n): ").lower().strip()
    download_logos = download_choice in ['y', 'yes', '1']
    
    if download_logos:
        print("✓ Will download logos to 'company_logos' folder")
    else:
        print("✓ Will only extract logo URLs")
    
    # Scrape Company Names and Logos
    print("\nStarting scraping process...")
    company_data = scrape_company_names_and_logos(download_logos=download_logos)
    
    if company_data:
        # Save to both formats
        save_to_json(company_data)
        # save_to_csv(company_data)
        
        # Print summary
        print_summary(company_data)
        
        # Show sample data
        print(f"\n=== SAMPLE DATA ===")
        if len(company_data) > 0:
            sample = company_data[0]
            for key, value in sample.items():
                print(f"{key}: {value}")
    else:
        print("No data was scraped.")
    
    print("\n=== Scraping Complete ===")

