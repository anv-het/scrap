# bellow code for the scrap all the atbles from the page

# import requests
# from bs4 import BeautifulSoup

# url = "https://www.investorgain.com/ipo/white-force/1315/"
# headers = {"User-Agent": "Mozilla/5.0"}
# res = requests.get(url, headers=headers)

# soup = BeautifulSoup(res.text, "html.parser")
# tables = soup.find_all("table")

# for table in tables:
#     # Look for first row to use as headers
#     rows = table.find_all("tr")
#     if not rows:
#         continue

#     headers = [cell.get_text(strip=True) for cell in rows[0].find_all(['th', 'td'])]

#     for row in rows[1:]:
#         cols = [cell.get_text(strip=True) for cell in row.find_all("td")]
#         if len(cols) == len(headers) and any(cols):
#             print(dict(zip(headers, cols)))


# now wrote code for the get this {'Incorporation': '2017', 'Sector': 'Other Consumer Services', 'IPO Issue Size': '₹22.06 Cr', 'Website': 'https://www.white-force.com/'} this data only from the page
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

# --- Headers for all requests ---
common_headers = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/91.0.4472.124 Safari/537.36"),
    "Accept": "application/json,text/html",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

# --- Get IPO list from the API ---
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
            print(f"⚠️ Unexpected API response: {data}")
            return []
    except requests.RequestException as e:
        print(f"❌ Error fetching IPO list: {e}")
        return []

# --- Scrape single IPO page for company info ---
def get_company_info(url):
    try:
        response = requests.get(url, headers=common_headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        tables = soup.find_all("table")
        expected_keys = {"Incorporation", "Sector", "IPO Issue Size", "Website"}

        for table in tables:
            rows = table.find_all("tr")
            if not rows or len(rows) < 2:
                continue

            header_cells = rows[0].find_all(['th', 'td'])
            headers_text = [cell.get_text(strip=True) for cell in header_cells]

            data_cells = rows[1].find_all("td")
            if not data_cells or len(data_cells) != len(headers_text):
                continue

            values = []
            for cell in data_cells:
                link = cell.find("a")
                values.append(link['href'] if link and link.has_attr('href') else cell.get_text(strip=True))

            result = dict(zip(headers_text, values))

            if expected_keys.issubset(result.keys()):
                return {key: result[key] for key in expected_keys}

            # fallback heuristic
            if len(headers_text) == 4 and "http" in values[-1] and "Cr" in values[-2]:
                return {
                    "Incorporation": values[0],
                    "Sector": values[1],
                    "IPO Issue Size": values[2],
                    "Website": values[3]
                }
        return None
    except Exception as e:
        print(f"❌ Error scraping {url}: {e}")
        return None

# --- Worker to scrape and combine data ---
def scrape_ipo_data(ipo):
    company_name = ipo.get("company_short_name", "N/A")
    ipo_id = ipo.get("id")
    folder_name = ipo.get("urlrewrite_folder_name")
    url = f"https://www.investorgain.com/ipo/{folder_name}/{ipo_id}/"

    company_info = get_company_info(url)

    if company_info is None:
        print(f"⚠️ Could not extract detailed info for {company_name} ({url})")
        company_info = {}

    # Combine API data + scraped info
    combined = {
        "id": ipo_id,
        "company_short_name": company_name,
        "ipo_status": ipo.get("ipo_status"),
        **company_info  # unpack scraped details if any
    }
    print(f"✅ Scraped {company_name}")
    return combined

# --- Save results to JSON ---
def save_to_json(data, filename="company_site.json"):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"\n💾 Data saved successfully to: {filename}")
    except IOError as e:
        print(f"❌ File write error: {e}")

# --- Main function ---
def main():
    ipo_list = fetch_ipo_list_from_api()
    if not ipo_list:
        print("⚠️ No IPO data found, exiting.")
        return

    results = []
    from concurrent.futures import ThreadPoolExecutor, as_completed

    max_workers = min(10, len(ipo_list))  # Limit concurrency sensibly
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(scrape_ipo_data, ipo): ipo for ipo in ipo_list}

        for future in as_completed(futures):
            ipo = futures[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"❌ Error processing IPO {ipo.get('company_short_name')}: {e}")

    save_to_json(results)

if __name__ == "__main__":
    main()
