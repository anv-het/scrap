import requests
from bs4 import BeautifulSoup
import json
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import retry, wait_random_exponential, stop_after_attempt, RetryError

# --- Config and headers ---
common_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

# --- Fetch IPO list from API ---
def fetch_ipo_list_from_api():
    api_url = "https://webnodejs.investorgain.com/cloud/ipo/list-read"
    try:
        print("🔄 Fetching IPO list from API...")
        response = requests.get(api_url, headers=common_headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get("msg") == 1 and "ipoList" in data:
            print(f"✅ Fetched {len(data['ipoList'])} IPOs.")
            return data["ipoList"]
        else:
            print(f"⚠️ API response not as expected: {data}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching IPO list from API: {e}")
        return []

# --- Robust request with retries ---
@retry(wait=wait_random_exponential(multiplier=0.5, min=1, max=4), stop=stop_after_attempt(3), reraise=True)
def make_robust_request(url):
    print(f"⏳ Requesting URL: {url}")
    time.sleep(random.uniform(0.5, 1.5))
    response = requests.get(url, headers=common_headers, timeout=15)
    response.raise_for_status()
    print(f"✅ Successfully fetched URL: {url}")
    return response.text

# --- Find peer comparison table robustly ---
def find_peer_comparison_table(soup):
    # Try 1: Find heading h2 containing "Peer Comparison" and then get next table
    for h2 in soup.find_all("h2"):
        if "Peer Comparison" in h2.get_text():
            print("🔍 Peer Comparison heading found via <h2> tag.")
            table = h2.find_next("table")
            if table:
                print("✅ Peer Comparison table found after heading.")
                return table

    # Try 2: Search all tables for expected headers
    expected_headers = {"Company", "EPS Basic", "EPS Diluted", "NAV", "P/E(x)", "RoNW", "Financial statements"}
    for table in soup.find_all("table"):
        headers = [th.get_text(strip=True) for th in table.find_all('th')]
        if expected_headers.issubset(set(headers)):
            print("🔍 Peer Comparison table found by matching headers.")
            return table

    print("⚠️ Peer Comparison table not found by any method.")
    return None

# --- Extract peer comparison data from the table ---
def extract_peer_comparison(soup):
    table = find_peer_comparison_table(soup)
    if not table:
        return {"error": "Peer comparison table not found."}

    headers = [th.get_text(strip=True) for th in table.find("thead").find_all("th")]
    rows = table.find("tbody").find_all("tr")

    data = []
    for row in rows:
        cols = row.find_all("td")
        row_data = {}
        # Map available columns to headers, even if counts mismatch
        for i in range(min(len(cols), len(headers))):
            row_data[headers[i]] = cols[i].get_text(strip=True)
        # If columns less than headers, missing keys won't be in dictionary (which is fine)
        data.append(row_data)

    print(f"✅ Extracted {len(data)} peer comparison rows.")
    return {"peer_comparison": data}


# --- Scrape peer comparison from a single IPO page ---
def scrape_peer_comparison(company_name, url, ipo_data):
    print(f"\n🌐 Starting scrape for {company_name}")
    result = {
        "id": ipo_data.get("id"),
        "urlrewrite_folder_name": ipo_data.get("urlrewrite_folder_name"),
        "urlrewrite_folder_name_main": ipo_data.get("urlrewrite_folder_name_main"),
        "ipo_status": ipo_data.get("ipo_status"),
        "company_name": company_name,
        "url": url,
        "peer_comparison": None,
        "error_message": None
    }
    try:
        html_content = make_robust_request(url)
        soup = BeautifulSoup(html_content, 'html.parser')
        peer_data = extract_peer_comparison(soup)
        if "error" in peer_data:
            result["error_message"] = peer_data["error"]
            print(f"❌ {company_name}: {peer_data['error']}")
        else:
            result["peer_comparison"] = peer_data["peer_comparison"]
            print(f"🎉 {company_name}: Peer comparison data scraped successfully.")
    except RetryError as e:
        err_msg = f"Retries failed: {str(e)}"
        result["error_message"] = err_msg
        print(f"❌ {company_name}: {err_msg}")
    except requests.exceptions.RequestException as e:
        err_msg = f"Request error: {str(e)}"
        result["error_message"] = err_msg
        print(f"❌ {company_name}: {err_msg}")
    except Exception as e:
        err_msg = f"Scraping exception: {str(e)}"
        result["error_message"] = err_msg
        print(f"❌ {company_name}: {err_msg}")
    return result

# --- Save to JSON ---
def save_to_json(data, filename="13_peer_comparison_data.json"):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"\n💾 Data saved successfully to: {filename}")
    except IOError as e:
        print(f"❌ File write error: {e}")

# --- Main execution ---
if __name__ == "__main__":
    print("=== Investorgain IPO Peer Comparison Scraper ===")
    ipo_list = fetch_ipo_list_from_api()
    if not ipo_list:
        print("⚠️ No IPOs found. Exiting.")
        exit(1)

    # Build URL map
    company_urls = {
        ipo['company_short_name']: f"https://www.investorgain.com/ipo/{ipo['urlrewrite_folder_name']}/{ipo['id']}/"
        for ipo in ipo_list
    }

    
    
    results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {}
        for ipo in ipo_list:
            name = ipo["company_short_name"]
            url = f"https://www.investorgain.com/ipo/{ipo['urlrewrite_folder_name']}/{ipo['id']}/"
            futures[executor.submit(scrape_peer_comparison, name, url, ipo)] = name

        for future in as_completed(futures):
            company_name = futures[future]
            try:
                result = future.result()
                if result["peer_comparison"]:
                    results.append(result)
            except Exception as e:
                print(f"❌ Error processing {company_name}: {e}")

    save_to_json(results)
    print("\n=== Scraping Completed === 🎉")
