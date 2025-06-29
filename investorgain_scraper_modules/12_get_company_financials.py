import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import re
import zlib
import brotli
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import retry, wait_random_exponential, stop_after_attempt, RetryError
import time
import random

# --- Configuration and Global Headers ---
proxies_list = []
USE_PROXIES = False

common_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

def fetch_ipo_list_from_api():
    api_url = "https://webnodejs.investorgain.com/cloud/ipo/list-read"
    try:
        response = requests.get(api_url, headers=common_headers, timeout=10)
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
    if text is None:
        return ""
    text = str(text).replace('\xa0', ' ').replace('\n', ' ').strip()
    return re.sub(r'\s+', ' ', text)

def convert_to_float(value):
    try:
        if value is None or not str(value).strip():
            return None
        cleaned_value = re.sub(r'[₹,$]', '', str(value)).replace(',', '')
        return float(cleaned_value)
    except (ValueError, TypeError):
        return None

@retry(wait=wait_random_exponential(multiplier=0.5, min=1, max=4), stop=stop_after_attempt(3), reraise=True)
def make_robust_request(url, custom_headers=None):
    request_headers = common_headers.copy()
    if custom_headers:
        request_headers.update(custom_headers)

    proxy = {"http": random.choice(proxies_list), "https": random.choice(proxies_list)} if USE_PROXIES and proxies_list else None
    time.sleep(random.uniform(0.5, 1.5))

    try:
        response = requests.get(url, headers=request_headers, timeout=15, proxies=proxy)
        response.raise_for_status()

        decoded_content = response.text

        if not decoded_content and response.content:
            content_encoding = response.headers.get('Content-Encoding')
            if content_encoding == 'gzip':
                decoded_content = zlib.decompress(response.content, 16 + zlib.MAX_WBITS).decode('utf-8', errors='ignore')
            elif content_encoding == 'br':
                decoded_content = brotli.decompress(response.content).decode('utf-8', errors='ignore')
            elif content_encoding == 'deflate':
                decoded_content = zlib.decompress(response.content, -zlib.MAX_WBITS).decode('utf-8', errors='ignore')
            else:
                decoded_content = response.content.decode('utf-8', errors='ignore')

        if not decoded_content:
            raise requests.exceptions.RequestException(f"Received empty content for {url}")

        return decoded_content

    except requests.exceptions.RequestException as e:
        print(f"  Request error for {url}: {e}")
        raise
    except (json.JSONDecodeError, zlib.error, brotli.Error) as e:
        print(f"  Decoding error for {url}: {e}")
        raise requests.exceptions.RequestException(f"Decoding error: {e}")

def scrape_and_format_financial_data(company_name, url):
    print(f"🌐 Scraping financial data for {company_name} from {url}")
    result = {
        "company_name": company_name,
        "url": url,
        "financial_data": None,
        "error_message": None
    }

    try:
        page_headers = {
            "Host": "www.investorgain.com",
            "Referer": "https://www.investorgain.com/ipo-list/"
        }

        html_content = make_robust_request(url, custom_headers=page_headers)
        soup = BeautifulSoup(html_content, 'html.parser')

        table = soup.find('table', {'id': 'financialTable'})
        if not table:
            result['error_message'] = "Financial table not found."
            return result

        rows = table.find_all('tr')
        data = []
        for row in rows:
            cols = [clean_text(col.get_text()) for col in row.find_all(['td', 'th'])]
            data.append(cols)

        if len(data) < 2:
            result['error_message'] = "Insufficient financial data."
            return result

        df = pd.DataFrame(data[1:], columns=data[0])
        output_formatted = []

        numeric_cols = df.columns[1:]

        for _, row in df.iterrows():
            metric = clean_text(row[df.columns[0]])
            entry = {"Metric": metric}
            for col in numeric_cols:
                val = convert_to_float(row[col])
                entry[col] = f"{val:.2f}" if val is not None else None
            output_formatted.append(entry)

        result["financial_data"] = {
            "Company Financial Information (Restated Consolidated)": output_formatted
        }

    except RetryError as e:
        result["error_message"] = f"Retries failed: {str(e)}"
    except requests.exceptions.RequestException as e:
        result["error_message"] = f"Request error: {str(e)}"
    except Exception as e:
        result["error_message"] = f"Scraping exception: {str(e)}"

    return result

def save_to_json(data, filename="company_financial_data.json"):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"✓ Data saved to: {filename}")
    except IOError as e:
        print(f"✗ File write error: {e}")

# --- Main Execution ---
if __name__ == "__main__":
    print("=== Investorgain Financial Data Scraper ===")
    ipo_list = fetch_ipo_list_from_api()

    if not ipo_list:
        print("⚠️ No IPOs found.")
        exit(1)

    company_urls = {
        ipo['company_short_name']: f"https://www.investorgain.com/ipo/{ipo['urlrewrite_folder_name']}/{ipo['id']}/"
        for ipo in ipo_list
    }

    results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(scrape_and_format_financial_data, name, url): name for name, url in company_urls.items()}

        for future in as_completed(futures):
            company_name = futures[future]
            try:
                result = future.result()
                if result["financial_data"]:
                    matched_ipo = next((ipo for ipo in ipo_list if ipo["company_short_name"] == company_name), None)
                    if matched_ipo:
                        output = {
                            "id": matched_ipo["id"],
                            "url": result["url"],
                            "urlrewrite_folder_name": matched_ipo["urlrewrite_folder_name"],
                            "urlrewrite_folder_name_main": "ipo",
                            "ipo_status": matched_ipo.get("ipo_status", ""),
                            "Company Financial Information (Restated Consolidated)": result["financial_data"]["Company Financial Information (Restated Consolidated)"]
                        }
                        results.append(output)
            except Exception as e:
                print(f"❌ Error processing {company_name}: {e}")

    save_to_json(results)
    print("=== Scraping Completed ===")
