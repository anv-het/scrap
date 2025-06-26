# import requests
# import json
# import pandas as pd
# from datetime import datetime
# import time
# import re
# from bs4 import BeautifulSoup
# import warnings
# warnings.filterwarnings('ignore')

# class IPODataScraper:
#     def __init__(self):
#         self.session = requests.Session()
#         self.setup_headers()
        
#     def setup_headers(self):
#         """Setup different headers for different sources"""
#         self.headers = {
#             'chittorgarh': {
#                 "Accept": "application/json, text/plain, */*",
#                 "Accept-Encoding": "gzip, deflate, br, zstd",
#                 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
#                 "Origin": "https://www.chittorgarh.com",
#                 "Referer": "https://www.chittorgarh.com/"
#             },
#             'investorgain': {
#                 "Accept": "application/json, text/plain, */*",
#                 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
#                 "Origin": "https://www.investorgain.com",
#                 "Referer": "https://www.investorgain.com/"
#             },
#             'moneycontrol': {
#                 "Accept": "application/json",
#                 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
#             }
#         }
    
#     def make_request(self, url, source, max_retries=3):
#         """Make HTTP request with proper headers and retry logic"""
#         headers = self.headers.get(source, {})
        
#         for attempt in range(max_retries):
#             try:
#                 response = self.session.get(url, headers=headers, timeout=30)
#                 response.raise_for_status()
#                 return response
#             except requests.exceptions.RequestException as e:
#                 print(f"Attempt {attempt + 1} failed for {source}: {str(e)}")
#                 if attempt < max_retries - 1:
#                     time.sleep(2 ** attempt)  # Exponential backoff
#                 else:
#                     print(f"Failed to fetch data from {url} after {max_retries} attempts")
#                     return None
    
#     def clean_html_text(self, text):
#         """Clean HTML tags and decode entities"""
#         if not text:
#             return ""
#         # Remove HTML tags
#         clean_text = re.sub('<.*?>', '', str(text))
#         # Decode HTML entities
#         clean_text = clean_text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
#         clean_text = clean_text.replace('&#8377;', '₹').replace('\u003C', '<').replace('\u003E', '>')
#         return clean_text.strip()
    
#     def extract_numeric_value(self, text):
#         """Extract numeric value from text"""
#         if not text:
#             return 0
#         numbers = re.findall(r'[\d,]+\.?\d*', str(text))
#         return float(numbers[0].replace(',', '')) if numbers else 0

#     # CHITTORGARH DATA METHODS
#     def get_chittorgarh_basic_ipos(self, ipo_type="all"):
#         """Get basic IPO details from Chittorgarh"""
#         print(f"Fetching Chittorgarh {ipo_type} IPO data...")
        
#         url = f"https://webnodejs.chittorgarh.com/cloud/report/data-read/82/1/6/2025/2025-26/0/{ipo_type}/0?search=&v=22-45"
        
#         response = self.make_request(url, 'chittorgarh')
#         if not response:
#             return []
        
#         try:
#             data = response.json()
#             ipos = []
            
#             for item in data.get('reportTableData', []):
#                 ipo = {
#                     'source': 'chittorgarh',
#                     'data_type': 'basic_info',
#                     'company_name': self.clean_html_text(item.get('Company', '')),
#                     'opening_date': item.get('Opening Date', ''),
#                     'closing_date': item.get('Closing Date', ''),
#                     'listing_date': item.get('Listing Date', ''),
#                     'issue_price': self.extract_numeric_value(item.get('Issue Price (Rs.)', 0)),
#                     'issue_amount_cr': self.extract_numeric_value(item.get('Issue Amount (Rs.cr.)', 0)),
#                     'listing_exchange': self.clean_html_text(item.get('Listing at', '')),
#                     'lead_manager': self.clean_html_text(item.get('Lead Manager', '')),
#                     'ipo_type': ipo_type,
#                     'url_slug': item.get('~URLRewrite_Folder_Name', ''),
#                     'scraped_at': datetime.now().isoformat()
#                 }
#                 ipos.append(ipo)
            
#             print(f"Successfully fetched {len(ipos)} {ipo_type} IPOs from Chittorgarh")
#             return ipos
            
#         except Exception as e:
#             print(f"Error parsing Chittorgarh {ipo_type} data: {str(e)}")
#             return []
    
#     def get_chittorgarh_subscriptions(self, board_type="mainboard"):
#         """Get subscription data from Chittorgarh"""
#         print(f"Fetching Chittorgarh {board_type} subscription data...")
        
#         report_id = "21" if board_type == "mainboard" else "22"
#         version = "21-22" if board_type == "mainboard" else "17-56"
        
#         url = f"https://webnodejs.chittorgarh.com/cloud/report/data-read/{report_id}/1/6/2025/2025-26/0/0/0?search=&v={version}"
        
#         response = self.make_request(url, 'chittorgarh')
#         if not response:
#             return []
        
#         try:
#             data = response.json()
#             subscriptions = []
            
#             for item in data.get('reportTableData', []):
#                 sub = {
#                     'source': 'chittorgarh',
#                     'data_type': 'subscription',
#                     'company_name': self.clean_html_text(item.get('Company Name', '')),
#                     'close_date': item.get('Close Date', ''),
#                     'size_cr': self.extract_numeric_value(item.get('Size (Rs Cr)', 0)),
#                     'qib_times': self.extract_numeric_value(item.get('QIB (x)', 0)),
#                     'nii_times': self.extract_numeric_value(item.get('NII (x)', 0)),
#                     'retail_times': self.extract_numeric_value(item.get('Retail (x)', 0)),
#                     'total_times': self.extract_numeric_value(item.get('Total (x)', 0)),
#                     'applications': self.extract_numeric_value(item.get('Applications', 0)),
#                     'board_type': board_type,
#                     'url_slug': item.get('~URLRewrite_Folder_Name', ''),
#                     'scraped_at': datetime.now().isoformat()
#                 }
                
#                 # Add additional fields for mainboard
#                 if board_type == "mainboard":
#                     sub.update({
#                         'snii_times': self.extract_numeric_value(item.get('sNII (x)', 0)),
#                         'bnii_times': self.extract_numeric_value(item.get('bNII (x)', 0)),
#                         'employee_times': self.extract_numeric_value(item.get('Employee (x)', 0)),
#                         'others_times': self.extract_numeric_value(item.get('Others (x)', 0))
#                     })
                
#                 subscriptions.append(sub)
            
#             print(f"Successfully fetched {len(subscriptions)} {board_type} subscriptions from Chittorgarh")
#             return subscriptions
            
#         except Exception as e:
#             print(f"Error parsing Chittorgarh {board_type} subscription data: {str(e)}")
#             return []

#     # INVESTORGAIN DATA METHODS
#     def get_investorgain_gmp(self, category="all"):
#         """Get GMP data from InvestorGain"""
#         print(f"Fetching InvestorGain {category} GMP data...")
        
#         url = f"https://webnodejs.investorgain.com/cloud/report/data-read/331/1/6/2025/2025-26/0/{category}?search=&v=23-18"
        
#         response = self.make_request(url, 'investorgain')
#         if not response:
#             return []
        
#         try:
#             data = response.json()
#             gmps = []
            
#             for item in data.get('reportTableData', []):
#                 gmp = {
#                     'source': 'investorgain',
#                     'data_type': 'gmp',
#                     'company_name': self.clean_html_text(item.get('Name', '')),
#                     'gmp_value': self.clean_html_text(item.get('GMP', '')),
#                     'fire_rating': self.clean_html_text(item.get('Fire Rating', '')),
#                     'subscription': self.clean_html_text(item.get('Sub', '')),
#                     'price': self.extract_numeric_value(item.get('Price', 0)),
#                     'est_listing': self.clean_html_text(item.get('Est Listing', '')),
#                     'ipo_size': self.clean_html_text(item.get('IPO Size', '')),
#                     'lot_size': self.extract_numeric_value(item.get('Lot', 0)),
#                     'pe_ratio': self.extract_numeric_value(item.get('~P/E', 0)),
#                     'open_date': item.get('Open', ''),
#                     'close_date': item.get('Close', ''),
#                     'boa_date': item.get('BoA Dt', ''),
#                     'listing_date': item.get('Listing', ''),
#                     'gmp_updated': item.get('GMP Updated', ''),
#                     'category': category,
#                     'ipo_category': item.get('~IPO_Category', ''),
#                     'url_slug': item.get('~urlrewrite_folder_name', ''),
#                     'scraped_at': datetime.now().isoformat()
#                 }
#                 gmps.append(gmp)
            
#             print(f"Successfully fetched {len(gmps)} {category} GMPs from InvestorGain")
#             return gmps
            
#         except Exception as e:
#             print(f"Error parsing InvestorGain {category} GMP data: {str(e)}")
#             return []
    
#     def get_investorgain_subscriptions(self):
#         """Get live subscription data from InvestorGain"""
#         print("Fetching InvestorGain subscription data...")
        
#         url = "https://webnodejs.investorgain.com/cloud/report/data-read/333/1/6/2025/2025-26/0/all?search=&v=23-51"
        
#         response = self.make_request(url, 'investorgain')
#         if not response:
#             return []
        
#         try:
#             data = response.json()
#             subscriptions = []
            
#             for item in data.get('reportTableData', []):
#                 sub = {
#                     'source': 'investorgain',
#                     'data_type': 'subscription',
#                     'company_name': self.clean_html_text(item.get('Name', '')),
#                     'total_subscription': self.clean_html_text(item.get('Total', '')),
#                     'bid_date': item.get('BID Date', ''),
#                     'qib': self.clean_html_text(item.get('QIB', '')),
#                     'shni': self.clean_html_text(item.get('SHNI', '')),
#                     'bhni': self.clean_html_text(item.get('BHNI', '')),
#                     'nii': self.clean_html_text(item.get('NII', '')),
#                     'rii': self.clean_html_text(item.get('RII', '')),
#                     'ipo_size': self.clean_html_text(item.get('IPO Size', '')),
#                     'ipo_price': self.extract_numeric_value(item.get('IPO Price', 0)),
#                     'lot_size': self.extract_numeric_value(item.get('Lot', 0)),
#                     'pe_ratio': self.extract_numeric_value(item.get('P/E', 0)),
#                     'close_date': item.get('Close Date', ''),
#                     'ipo_category': item.get('~IPO_Category', ''),
#                     'url_slug': item.get('~URLRewrite_Folder_Name', ''),
#                     'scraped_at': datetime.now().isoformat()
#                 }
#                 subscriptions.append(sub)
            
#             print(f"Successfully fetched {len(subscriptions)} subscriptions from InvestorGain")
#             return subscriptions
            
#         except Exception as e:
#             print(f"Error parsing InvestorGain subscription data: {str(e)}")
#             return []
    
#     def get_investorgain_performance(self):
#         """Get IPO performance data from InvestorGain"""
#         print("Fetching InvestorGain performance data...")
        
#         url = "https://webnodejs.investorgain.com/cloud/report/data-read/377/1/6/2025/2025-26/0/all?search=&v=22-50"
        
#         response = self.make_request(url, 'investorgain')
#         if not response:
#             return []
        
#         try:
#             data = response.json()
#             performances = []
            
#             for item in data.get('reportTableData', []):
#                 perf = {
#                     'source': 'investorgain',
#                     'data_type': 'performance',
#                     'ipo_name': self.clean_html_text(item.get('IPO', '')),
#                     'listing_date': item.get('Listing Date', ''),
#                     'ipo_size': self.clean_html_text(item.get('IPO_Size', '')),
#                     'subscription': self.clean_html_text(item.get('Subscription', '')),
#                     'gmp': self.clean_html_text(item.get('GMP', '')),
#                     'ipo_price': self.extract_numeric_value(item.get('IPO Price', 0)),
#                     'estimated_price': self.extract_numeric_value(item.get('Estimated Price', 0)),
#                     'listing_price': self.extract_numeric_value(item.get('Listing Price', 0)),
#                     'closing_price': self.extract_numeric_value(item.get('Closing Price', 0)),
#                     'ltp': self.extract_numeric_value(item.get('LTP', 0)),
#                     'last_updated': item.get('~Last Updated', ''),
#                     'ipo_category': item.get('~IPO_Category', ''),
#                     'url_slug': item.get('~URLRewrite_Folder_Name', ''),
#                     'scraped_at': datetime.now().isoformat()
#                 }
#                 performances.append(perf)
            
#             print(f"Successfully fetched {len(performances)} performance records from InvestorGain")
#             return performances
            
#         except Exception as e:
#             print(f"Error parsing InvestorGain performance data: {str(e)}")
#             return []
    
#     def get_investorgain_calendar(self):
#         """Get IPO calendar from InvestorGain"""
#         print("Fetching InvestorGain calendar data...")
        
#         url = "https://webnodejs.investorgain.com/cloud/report/data-read/554/1/6/2025/2025-26/0/0?search=&v=23-50"
        
#         response = self.make_request(url, 'investorgain')
#         if not response:
#             return []
        
#         try:
#             data = response.json()
#             calendar_events = []
            
#             for item in data.get('reportTableData', []):
#                 event = {
#                     'source': 'investorgain',
#                     'data_type': 'calendar',
#                     'date': item.get('Date', ''),
#                     'day': item.get('Day', ''),
#                     'open_events': self.clean_html_text(item.get('Open', '')),
#                     'close_events': self.clean_html_text(item.get('Close', '')),
#                     'unblock_events': self.clean_html_text(item.get('Unblock (stock names)', '')),
#                     'listing_events': self.clean_html_text(item.get('Listing', '')),
#                     'scraped_at': datetime.now().isoformat()
#                 }
#                 calendar_events.append(event)
            
#             print(f"Successfully fetched {len(calendar_events)} calendar events from InvestorGain")
#             return calendar_events
            
#         except Exception as e:
#             print(f"Error parsing InvestorGain calendar data: {str(e)}")
#             return []

#     # MONEYCONTROL DATA METHODS
#     def get_moneycontrol_calendar(self):
#         """Get IPO calendar from MoneyControl"""
#         print("Fetching MoneyControl calendar data...")
        
#         url = "https://api.moneycontrol.com/mcapi/v1/ipo/calendar-data"
        
#         response = self.make_request(url, 'moneycontrol')
#         if not response:
#             return []
        
#         try:
#             data = response.json()
#             calendar_events = []
            
#             for item in data:
#                 event = {
#                     'source': 'moneycontrol',
#                     'data_type': 'calendar',
#                     'date': item.get('date', ''),
#                     'type': item.get('type', ''),
#                     'company_name': item.get('company_name', ''),
#                     'color_code': item.get('color_code', ''),
#                     'open_date': item.get('open_date', ''),
#                     'close_date': item.get('close_date', ''),
#                     'allotment_date': item.get('allotment_date', ''),
#                     'refund_date': item.get('refund_date', ''),
#                     'credit_to_demat_date': item.get('credit_to_demat_date', ''),
#                     'listing_date': item.get('listing_date', ''),
#                     'sc_did': item.get('sc_did', ''),
#                     'url': item.get('url', ''),
#                     'scraped_at': datetime.now().isoformat()
#                 }
#                 calendar_events.append(event)
            
#             print(f"Successfully fetched {len(calendar_events)} calendar events from MoneyControl")
#             return calendar_events
            
#         except Exception as e:
#             print(f"Error parsing MoneyControl calendar data: {str(e)}")
#             return []

#     def scrape_all_data(self):
#         """Scrape all IPO data from all sources"""
#         print("=" * 60)
#         print("🚀 Starting Complete IPO Data Scraping...")
#         print("=" * 60)
        
#         all_data = {
#             'basic_ipos': [],
#             'subscriptions': [],
#             'gmp_data': [],
#             'performance_data': [],
#             'calendar_events': []
#         }
        
#         # Rate limiting between requests
#         delay = 1
        
#         try:
#             # CHITTORGARH DATA
#             print("\n📊 CHITTORGARH DATA")
#             print("-" * 30)
            
#             # Basic IPO data
#             for ipo_type in ['all', 'mainboard', 'sme']:
#                 all_data['basic_ipos'].extend(self.get_chittorgarh_basic_ipos(ipo_type))
#                 time.sleep(delay)
            
#             # Subscription data
#             for board_type in ['mainboard', 'sme']:
#                 all_data['subscriptions'].extend(self.get_chittorgarh_subscriptions(board_type))
#                 time.sleep(delay)
            
#             # INVESTORGAIN DATA
#             print("\n💰 INVESTORGAIN DATA")
#             print("-" * 30)
            
#             # GMP data
#             for category in ['all', 'ipo', 'sme', 'current', 'close', 'listed']:
#                 all_data['gmp_data'].extend(self.get_investorgain_gmp(category))
#                 time.sleep(delay)
            
#             # Subscription data
#             all_data['subscriptions'].extend(self.get_investorgain_subscriptions())
#             time.sleep(delay)
            
#             # Performance data
#             all_data['performance_data'].extend(self.get_investorgain_performance())
#             time.sleep(delay)
            
#             # Calendar data
#             all_data['calendar_events'].extend(self.get_investorgain_calendar())
#             time.sleep(delay)
            
#             # MONEYCONTROL DATA
#             print("\n📅 MONEYCONTROL DATA")
#             print("-" * 30)
            
#             # Calendar data
#             all_data['calendar_events'].extend(self.get_moneycontrol_calendar())
            
#             print("\n" + "=" * 60)
#             print("✅ DATA SCRAPING COMPLETED!")
#             print("=" * 60)
            
#             # Print summary
#             print(f"📈 Basic IPO Records: {len(all_data['basic_ipos'])}")
#             print(f"📊 Subscription Records: {len(all_data['subscriptions'])}")
#             print(f"💰 GMP Records: {len(all_data['gmp_data'])}")
#             print(f"📉 Performance Records: {len(all_data['performance_data'])}")
#             print(f"📅 Calendar Events: {len(all_data['calendar_events'])}")
#             print(f"🎯 Total Records: {sum(len(v) for v in all_data.values())}")
            
#             return all_data
            
#         except Exception as e:
#             print(f"\n❌ Error during scraping: {str(e)}")
#             return all_data
    
#     def save_to_files(self, data, format='json'):
#         """Save scraped data to files"""
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
#         if format.lower() == 'json':
#             filename = f"ipo_data_{timestamp}.json"
#             with open(filename, 'w', encoding='utf-8') as f:
#                 json.dump(data, f, indent=2, ensure_ascii=False)
#             print(f"💾 Data saved to {filename}")
        
#         elif format.lower() == 'csv':
#             for data_type, records in data.items():
#                 if records:
#                     df = pd.DataFrame(records)
#                     filename = f"ipo_{data_type}_{timestamp}.csv"
#                     df.to_csv(filename, index=False, encoding='utf-8')
#                     print(f"💾 {data_type} saved to {filename}")
        
#         return timestamp

# # USAGE EXAMPLE
# if __name__ == "__main__":
#     # Initialize scraper
#     scraper = IPODataScraper()
    
#     # Scrape all data
#     scraped_data = scraper.scrape_all_data()
    
#     # Save to files
#     timestamp = scraper.save_to_files(scraped_data, format='json')
#     scraper.save_to_files(scraped_data, format='csv')
    
#     print(f"\n🎉 Scraping completed! Files saved with timestamp: {timestamp}")



# Save this code as ipo_scraper.py
import requests
from bs4 import BeautifulSoup
import json
import time
import re
import csv # Import the csv module

def fetch_ipo_list_from_api():
    """
    Fetches the list of IPOs from the Investorgain API.
    """
    api_url = "https://webnodejs.investorgain.com/cloud/ipo/list-read"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(api_url, headers=headers)
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
    ipo_name_tag = soup.find('div', class_='col-lg-6').find('h1')
    if ipo_name_tag:
        ipo_details['IPO Name'] = clean_text(ipo_name_tag.get_text(strip=True))
    else:
        ipo_details['IPO Name'] = 'N/A'

    # 2. Company Logo
    logo_img_tag = soup.find('div', class_='div-logo').find('img')
    if logo_img_tag:
        ipo_details['Company Logo URL'] = logo_img_tag.get('src')

    # 3. IPO Overview Paragraphs
    overview_div = soup.find('div', class_='float-none mb-2 ms-2')
    if overview_div:
        paragraphs = overview_div.find_all('p')
        ipo_details['IPO Overview'] = " ".join([clean_text(p.get_text(strip=True)) for p in paragraphs]) # Join for CSV
        # You can parse specific elements from these paragraphs more rigorously if needed

    # 4. IPO Details Table (Cedaar Textile SME IPO Details)
    ipo_detail_table_header = soup.find('h2', itemprop='about', string=lambda s: "SME IPO Details" in s)
    if ipo_detail_table_header:
        detail_table = ipo_detail_table_header.find_next_sibling('table', class_='table table-bordered table-striped table-hover w-auto')
        if detail_table:
            rows = detail_table.find('tbody').find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) == 2:
                    key = clean_text(cols[0].get_text(strip=True)).replace(':', '')
                    value_tag = cols[1]
                    if 'DRHP' in key or 'RHP' in key:
                        link_tag = value_tag.find('a')
                        if link_tag:
                            ipo_details[key] = link_tag.get('href')
                        else:
                            ipo_details[key] = clean_text(value_tag.get_text(strip=True))
                    else:
                        ipo_details[key] = clean_text(value_tag.get_text(strip=True))

    # 5. Important Dates Table
    dates_table_header = soup.find('h2', itemprop='about', string=lambda s: "SME IPO Important Dates" in s)
    if dates_table_header:
        dates_table = dates_table_header.find_next_sibling('table', class_='table table-bordered table-striped table-hover w-auto')
        if dates_table:
            rows = dates_table.find('tbody').find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) == 2:
                    key = clean_text(cols[0].get_text(strip=True)).replace('*', '').replace(':', '')
                    value = clean_text(cols[1].get_text(strip=True))
                    ipo_details[f'Important Date - {key}'] = value # Flatten for CSV

    # 6. IPO Lots Table
    lots_table_header = soup.find('h2', itemprop='about', string=lambda s: "SME IPO Lots" in s)
    if lots_table_header:
        lots_table = lots_table_header.find_next_sibling('table', class_='table table-bordered table-striped table-hover w-auto')
        if lots_table:
            rows = lots_table.find('tbody').find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) == 2:
                    key = clean_text(cols[0].get_text(strip=True)).replace(':', '')
                    value = clean_text(cols[1].get_text(strip=True))
                    ipo_details[f'IPO Lot - {key}'] = value # Flatten for CSV

    # 7. IPO GMP Table
    gmp_table_header = soup.find('h2', itemprop='about', string=lambda s: 'IPO GMP' in s or 'Live GMP' in s)
    if not gmp_table_header:
        gmp_table_header = soup.find('h3', itemprop='about', string=lambda s: 'IPO GMP' in s or 'Live GMP' in s)

    if gmp_table_header:
        gmp_table = gmp_table_header.find_next_sibling('table', class_='table table-bordered table-striped w-auto')
        if gmp_table:
            headers = [clean_text(th.get_text(strip=True)) for th in gmp_table.find('thead').find_all('th')]
            rows = gmp_table.find('tbody').find_all('tr')
            # For CSV, we'll just take the latest GMP or concatenate
            latest_gmp = {}
            if rows:
                cols = rows[0].find_all('td') # Assuming first row is latest
                for i, col in enumerate(cols):
                    if i < len(headers):
                        latest_gmp[headers[i]] = clean_text(col.get_text(strip=True))
            ipo_details['Latest GMP Update'] = json.dumps(latest_gmp) # Store as JSON string in CSV cell

    # 8. About Company Section
    about_company_h3 = soup.find('h3', itemprop='about', string=lambda s: 'About Company' in s)
    if about_company_h3:
        about_company_div = about_company_h3.find_parent('div', class_='col-12')
        if about_company_div:
            description_paragraphs_div = about_company_div.find('div', class_=False, recursive=False)
            if description_paragraphs_div:
                ipo_details['About Company Description'] = " ".join([clean_text(p.get_text(strip=True)) for p in description_paragraphs_div.find_all('p')])

            strengths_h3 = about_company_div.find('h3', string=lambda s: 'Strengths' in s)
            if strengths_h3:
                strengths_div = strengths_h3.find_next_sibling('div')
                if strengths_div:
                    ipo_details['Company Strengths'] = "; ".join([clean_text(li.get_text(strip=True)) for li in strengths_div.find_all('li')])

            company_info_table = about_company_div.find('table', class_='table table-bordered table-striped table-hover w-auto')
            if company_info_table:
                headers = [clean_text(td.get_text(strip=True)) for td in company_info_table.find('thead').find_all('td')]
                data_row = company_info_table.find('tbody').find('tr')
                if data_row:
                    cols = data_row.find_all('td')
                    for i, header in enumerate(headers):
                        if i < len(cols):
                            if header == 'Website':
                                link_tag = cols[i].find('a')
                                ipo_details[f'Company Info - {header}'] = link_tag.get('href') if link_tag else clean_text(cols[i].get_text(strip=True))
                            else:
                                ipo_details[f'Company Info - {header}'] = clean_text(cols[i].get_text(strip=True))

    # 9. IPO Objective Section
    objective_h3 = soup.find('h3', itemprop='about', string=lambda s: 'Objective' in s)
    if objective_h3:
        objective_table_div = objective_h3.find_next_sibling('div', class_='table-responsive')
        if objective_table_div:
            objective_table = objective_table_div.find('table', id='ObjectiveIssue')
            if objective_table:
                objective_data = []
                rows = objective_table.find('tbody').find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 3:
                        objective_data.append(f"{clean_text(cols[0].get_text(strip=True))}: {clean_text(cols[1].get_text(strip=True))} ({clean_text(cols[2].get_text(strip=True))} Cr)")
                ipo_details['IPO Objective'] = "; ".join(objective_data)


    # 10. Subscription Data, Financials, and Peer Comparison
    subscription_h2 = soup.find('h2', itemprop='about', string=lambda s: 'Live Subscription' in s)
    if subscription_h2:
        parent_div = subscription_h2.find_parent('div', class_='col-12')
        if parent_div:
            ul_shares = parent_div.find('ul')
            if ul_shares:
                ipo_details['Subscription Share Distribution'] = "; ".join([clean_text(li.get_text(strip=True)) for li in ul_shares.find_all('li')])

            bidding_table = parent_div.find('table', class_='table table-bordered table-striped table-hover w-auto')
            if bidding_table:
                bidding_headers = [clean_text(th.get_text(strip=True)) for th in bidding_table.find('thead').find_all('th')]
                bidding_data = []
                tbody_rows = bidding_table.find('tbody').find_all('tr')
                for row in tbody_rows:
                    row_data = []
                    cols = row.find_all('td')
                    for i, col in enumerate(cols):
                        if i < len(bidding_headers):
                            row_data.append(f"{bidding_headers[i] if bidding_headers[i].strip() else f'Col_{i}'}: {clean_text(col.get_text(strip=True))}")
                    if row_data:
                        bidding_data.append(" | ".join(row_data))
                ipo_details['IPO Bidding Live Updates'] = "; ".join(bidding_data)

    financial_h2 = soup.find('h2', itemprop='about', string=lambda s: 'Financial Information (Restated)' in s)
    if financial_h2:
        financial_table_div = financial_h2.find_next_sibling('div', class_='table-responsive')
        if financial_table_div:
            financial_table = financial_table_div.find('table', id='financialTable')
            if financial_table:
                period_headers = [clean_text(td.get_text(strip=True)) for td in financial_table.find('tbody').find('tr').find_all('td')]
                financial_data_rows = financial_table.find('tbody').find_all('tr')[1:]
                for row in financial_data_rows:
                    cols = row.find_all('td')
                    if cols:
                        metric_name = clean_text(cols[0].get_text(strip=True))
                        for i, period in enumerate(period_headers[1:], start=1):
                            if i < len(cols):
                                ipo_details[f'Financial - {metric_name} ({period})'] = clean_text(cols[i].get_text(strip=True))

    peer_h2 = soup.find('h2', itemprop='about', string=lambda s: 'Peer Comparison' in s)
    if peer_h2:
        peer_table_div = peer_h2.find_next_sibling('div', class_='table-responsive')
        if peer_table_div:
            peer_table = peer_table_div.find('table', class_='table table-bordered table-striped table-hover w-auto')
            if peer_table:
                headers = [clean_text(th.get_text(strip=True)) for th in peer_table.find('thead').find_all('th')]
                peer_data = []
                rows = peer_table.find('tbody').find_all('tr')
                for row in rows:
                    entry_data = []
                    cols = row.find_all('td')
                    for i, col in enumerate(cols):
                        if i < len(headers):
                            entry_data.append(f"{headers[i]}: {clean_text(col.get_text(strip=True))}")
                    if entry_data:
                        peer_data.append(" | ".join(entry_data))
                ipo_details['Peer Comparison'] = "; ".join(peer_data)

    # 11. Company Address, Registrar, Lead Manager
    contact_info_row = soup.find('div', class_='row').find_all('div', class_=re.compile(r'col-lg-4|col-md-4|col-sm-4'))
    for col_div in contact_info_row:
        header = col_div.find('h3')
        if header:
            header_text = clean_text(header.get_text(strip=True))
            card_body = col_div.find('div', class_='card-body')
            if card_body:
                if 'Company Address' in header_text:
                    # Flatten address details for CSV
                    company_address_info_text = ""
                    lines = [clean_text(p) for p in card_body.get_text(separator='\n').split('\n') if clean_text(p)]
                    company_address_info_text += f"Name: {clean_text(card_body.find('strong').get_text(strip=True)) if card_body.find('strong') else 'N/A'}; "
                    company_address_info_text += f"Address: {' '.join(lines[1:-3]) if len(lines) > 4 else 'N/A'}; "
                    company_address_info_text += f"City_State_Pincode_Country: {lines[-3] if len(lines) > 3 else 'N/A'}; "
                    website_tag = card_body.find('a', href=True)
                    company_address_info_text += f"Website: {website_tag['href'] if website_tag else 'N/A'}; "
                    phone_match = re.search(r'Phone\s*:\s*([+\d\s-]+)', card_body.get_text())
                    company_address_info_text += f"Phone: {phone_match.group(1).strip() if phone_match else 'N/A'}; "
                    email_match = re.search(r'Email\s*:\s*(\S+@\S+)', card_body.get_text())
                    company_address_info_text += f"Email: {email_match.group(1).strip() if email_match else 'N/A'}"
                    ipo_details['Company Address'] = company_address_info_text

                elif 'Registrar' in header_text:
                    # Flatten registrar details for CSV
                    registrar_info_text = ""
                    lines = [clean_text(p) for p in card_body.get_text(separator='\n').split('\n') if clean_text(p)]
                    registrar_info_text += f"Name: {clean_text(card_body.find('strong').get_text(strip=True)) if card_body.find('strong') else 'N/A'}; "
                    registrar_info_text += f"Address: {' '.join(lines[1:-3]) if len(lines) > 4 else 'N/A'}; "
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
                        link = li.find('a')
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

    for i, ipo_entry in enumerate(ipo_list): # Iterate through all IPOs
        company_short_name = ipo_entry.get('company_short_name')
        url_rewrite_folder_name = ipo_entry.get('urlrewrite_folder_name')
        ipo_category = ipo_entry.get('ipo_category')

        if not url_rewrite_folder_name:
            print(f"Skipping {company_short_name} due to missing URL folder name.")
            continue

        detail_url = f"{base_url}/ipo/{url_rewrite_folder_name}/{ipo_entry.get('id')}/"


        print(f"\nScraping details for {company_short_name} ({ipo_category} IPO) from: {detail_url}")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        try:
            response = requests.get(detail_url, headers=headers)
            response.raise_for_status() # Raise an exception for HTTP errors
            soup = BeautifulSoup(response.content, 'html.parser')
            detailed_data = parse_ipo_detail_page(soup)
            all_ipo_data.append({**ipo_entry, **detailed_data}) # Merge API data with scraped data
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
    It flattens nested dictionaries for CSV compatibility.
    """
    if not data:
        print("No data to save to CSV.")
        return

    # Determine all unique fieldnames (headers)
    fieldnames = set()
    for row in data:
        fieldnames.update(row.keys())

    # Sort fieldnames for consistent column order
    fieldnames = sorted(list(fieldnames))

    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                # Ensure all fields are present for DictWriter, fill missing with empty string
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
        print(f"\nScraping complete! Data saved to '{json_filename}'")

        # Save to CSV file
        csv_filename = "ipo_details.csv"
        save_to_csv(scraped_data, csv_filename)
    else:
        print("No data was scraped.")
