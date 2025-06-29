import requests
from bs4 import BeautifulSoup
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import re # Import re for flexible text cleaning
import zlib # For gzip decompression
import brotli # For brotli decompression (install with: pip install brotli)

# Comprehensive headers to mimic a browser for both API and detail pages
common_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1" # For HTML pages
}

# Define a robust clean_text function
def clean_text(text):
    """
    Cleans extracted text by removing extra spaces, newlines, non-breaking spaces,
    and consolidating multiple spaces.
    """
    if text:
        text = text.replace('\xa0', ' ').replace('\n', ' ').strip()
        text = re.sub(r'\s+', ' ', text) # Replace multiple spaces with a single space
    return text

# Step 1: Get IPO list (Updated to use more robust fetching)
def fetch_ipo_list_from_api():
    api_url = 'https://webnodejs.investorgain.com/cloud/ipo/list-read'
    headers_api = common_headers.copy()
    headers_api["Host"] = "webnodejs.investorgain.com"
    headers_api["Referer"] = "https://www.investorgain.com/"
    headers_api["Accept"] = "*/*" # API typically accepts any
    headers_api["Sec-Fetch-Dest"] = "empty"
    headers_api["Sec-Fetch-Mode"] = "cors"
    headers_api["Sec-Fetch-Site"] = "same-site"

    try:
        resp = requests.get(api_url, headers=headers_api, timeout=15)
        resp.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

        # Attempt to decode JSON, with fallbacks for compression
        try:
            data = resp.json()
        except json.JSONDecodeError:
            content_encoding = resp.headers.get('Content-Encoding')
            if content_encoding == 'gzip':
                data = json.loads(zlib.decompress(resp.content, 16 + zlib.MAX_WBITS).decode('utf-8'))
            elif content_encoding == 'br':
                data = json.loads(brotli.decompress(resp.content).decode('utf-8'))
            else:
                raise # Re-raise if no known compression or decoding issue

        if data.get('msg') == 1 and 'ipoList' in data:
            return data['ipoList']
        else:
            print(f"API response not as expected: {data}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Error fetching IPO list from API: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred during API fetch: {e}")
        return []

ipo_data = fetch_ipo_list_from_api()

# Step 2: Define scraper function
def fetch_ipo_strengths(ipo):
    try:
        ipo_id = ipo['id']
        slug = ipo['urlrewrite_folder_name']
        company_name = ipo['company_short_name']
        detail_url = f"https://www.investorgain.com/ipo/{slug}-ipo/{ipo_id}/"

        headers_detail = common_headers.copy()
        headers_detail["Host"] = "www.investorgain.com"
        headers_detail["Referer"] = "https://www.investorgain.com/ipo-list/"
        headers_detail["Sec-Fetch-Dest"] = "document"
        headers_detail["Sec-Fetch-Mode"] = "navigate"
        headers_detail["Sec-Fetch-Site"] = "same-origin"

        res = requests.get(detail_url, headers=headers_detail, timeout=10)
        res.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

        # Fallback for decompression if requests.text is empty
        html_content = res.text
        if not html_content and res.content:
            content_encoding = res.headers.get('Content-Encoding')
            if content_encoding == 'gzip':
                html_content = zlib.decompress(res.content, 16 + zlib.MAX_WBITS).decode('utf-8')
            elif content_encoding == 'br':
                html_content = brotli.decompress(res.content).decode('utf-8')

        soup = BeautifulSoup(html_content, 'html.parser')

        strengths = []
        # MODIFIED: Search for any H3 tag containing "Strengths" (case-insensitive)
        for h3 in soup.find_all('h3'):
            cleaned_h3_text = clean_text(h3.get_text()) # Clean H3 text before checking
            if re.search(r'strengths', cleaned_h3_text, re.IGNORECASE): # Case-insensitive search
                div = h3.find_next_sibling('div')
                if div:
                    ul = div.find('ul')
                    if ul:
                        # Use clean_text for each list item
                        strengths = [clean_text(li.get_text()) for li in ul.find_all('li') if clean_text(li.get_text())]
                        break # Found the strengths, no need to check other h3s
        
        # MODIFIED: Return empty list if no strengths found, or the actual strengths
        return {
            "company_name": company_name,
            "data": {
                "id": ipo_id,
                "url": detail_url,
                "urlrewrite_folder_name": slug,
                "urlrewrite_folder_name_main": ipo.get("urlrewrite_folder_name_main", ""),
                "ipo_status": ipo.get("ipo_status", ""),
                "strengths": strengths # Return empty list if nothing found
            }
        }

    except Exception as e:
        print(f"Error processing IPO {ipo.get('company_short_name', 'Unknown')} (ID: {ipo.get('id', '')}): {str(e)}")
        return {
            "company_name": ipo.get("company_short_name", "Unknown"),
            "data": {
                "id": ipo.get("id", ""),
                "url": "",
                "urlrewrite_folder_name": ipo.get("urlrewrite_folder_name", ""),
                "urlrewrite_folder_name_main": ipo.get("urlrewrite_folder_name_main", ""),
                "ipo_status": ipo.get("ipo_status", ""),
                "strengths": [f"Error fetching/parsing strengths: {str(e)}"] # Specific error message
            }
        }

# Step 3: Use concurrent fetching
results = {}
if ipo_data: # Only proceed if ipo_data was fetched successfully
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_ipo = {executor.submit(fetch_ipo_strengths, ipo): ipo for ipo in ipo_data}
        for future in as_completed(future_to_ipo):
            result = future.result()
            results[result["company_name"]] = result["data"]
            # Only print fetched status, error messages are handled within fetch_ipo_strengths
            if not result["data"]["strengths"] or "Error:" not in result["data"]["strengths"][0]:
                print(f"✔ Fetched strengths for: {result['company_name']}")
            else:
                print(f"⚠️ Processed with error for: {result['company_name']}")

# Step 4: Save to JSON
if results: # Only save if there are results
    with open('ipo_strengths_detailed.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("✅ Done. Saved to 'ipo_strengths_detailed.json'")
else:
    print("❌ No data to save. Script might have encountered errors fetching IPO list.")

print("=== Script Complete ===")

