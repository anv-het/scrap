import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import retry, wait_random_exponential, stop_after_attempt
import time
import random
import json
from datetime import datetime


headers = {'User-Agent': 'Mozilla/5.0'}
ipo_list_api = 'https://webnodejs.investorgain.com/cloud/ipo/list-read'

# Optional: List of proxies (rotate randomly)
proxies_list = [
    # 'http://user:pass@proxy1:port',
    # 'http://user:pass@proxy2:port'
]
USE_PROXIES = False

# Retry logic: max 3 attempts, exponential backoff
@retry(wait=wait_random_exponential(min=1, max=4), stop=stop_after_attempt(3))
def safe_request(url):
    proxy = {"http": random.choice(proxies_list), "https": random.choice(proxies_list)} if USE_PROXIES else None
    return requests.get(url, headers=headers, timeout=10, proxies=proxy)

def extract_ipo_objectives(soup):
    objectives = []
    try:
        for h3 in soup.find_all("h3"):
            if "IPO Objective" in h3.get_text():
                table = soup.find("table", {"id": "ObjectiveIssue"})
                if not table:
                    break
                rows = table.find("tbody").find_all("tr")
                for row in rows:
                    cols = row.find_all("td")
                    if len(cols) >= 2:
                        objectives.append({
                            "s_no": cols[0].get_text(strip=True),
                            "object": cols[1].get_text(strip=True),
                            "amount": cols[2].get_text(strip=True) if len(cols) > 2 else ""
                        })
                break
    except Exception as e:
        objectives.append({"error": str(e)})
    return objectives

def fetch_ipo_details(ipo):
    try:
        # Throttle each thread slightly to avoid hammering
        time.sleep(random.uniform(1, 2))

        ipo_id = ipo['id']
        slug = ipo['urlrewrite_folder_name']
        company_name = ipo['company_short_name']
        detail_url = f"https://www.investorgain.com/ipo/{slug}/{ipo_id}/"
        print(f"🔍 Scraping details for: {company_name} ({detail_url})")
        res = safe_request(detail_url)
        soup = BeautifulSoup(res.text, 'html.parser')

        # Extract Strengths
        strengths = []
        for h3 in soup.find_all('h3'):
            if 'IPO Strengths' in h3.get_text():
                div = h3.find_next_sibling('div')
                if div:
                    ul = div.find('ul')
                    if ul:
                        strengths = [li.get_text(strip=True) for li in ul.find_all('li')]
                break

        # Extract Objectives
        objectives = extract_ipo_objectives(soup)

        return {
            "company_name": company_name,
            "data": {
                "id": ipo_id,
                "url": detail_url,
                "urlrewrite_folder_name": slug,
                "urlrewrite_folder_name_main": ipo.get("urlrewrite_folder_name_main", ""),
                "ipo_status": ipo.get("ipo_status", ""),
                "strengths": strengths or ["No IPO Strengths found"],
                "objectives": objectives or ["No IPO Objectives found"],
                "scraped_at": datetime.now().isoformat()
            }
        }

    except Exception as e:
        return {
            "company_name": ipo.get("company_short_name", "Unknown"),
            "data": {
                "id": ipo.get("id", ""),
                "url": "",
                "urlrewrite_folder_name": ipo.get("urlrewrite_folder_name", ""),
                "urlrewrite_folder_name_main": ipo.get("urlrewrite_folder_name_main", ""),
                "ipo_status": ipo.get("ipo_status", ""),
                "strengths": [f"Error: {str(e)}"],
                "objectives": [f"Error: {str(e)}"],
                "scraped_at": datetime.now().isoformat()
            }
        }

def scrape_all_ipo_data():
    print("📡 Fetching IPO list...")
    resp = requests.get(ipo_list_api, headers=headers)
    ipo_data = resp.json().get('ipoList', [])

    results = {}
    print(f"🔍 Found {len(ipo_data)} IPOs. Scraping each...")

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_ipo = {executor.submit(fetch_ipo_details, ipo): ipo for ipo in ipo_data}
        for future in as_completed(future_to_ipo):
            result = future.result()
            results[result["company_name"]] = result["data"]
            print(f"✔ Done: {result['company_name']}")

    return results

if __name__ == "__main__":
    all_ipo_data = scrape_all_ipo_data()

    with open('ipo_strengths_objectives_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_ipo_data, f, ensure_ascii=False, indent=2)

    print("\n✅ All IPO Strengths & Objectives saved to 'ipo_strengths_objectives_data.json'")
