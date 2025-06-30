import requests
from bs4 import BeautifulSoup
import re
import json
# -------------------------------
# STEP 1: Get all IPOs from API
# -------------------------------
def fetch_all_ipos():
    url = "https://webnodejs.investorgain.com/cloud/ipo/list-read"
    try:
        response = requests.get(url)
        data = response.json()

        if data.get("msg") == 1 and "ipoList" in data:
            return data["ipoList"]
        else:
            print("Failed to fetch IPO list.")
            return []
    except Exception as e:
        print(f"Error fetching IPO list: {e}")
        return []

# ----------------------------------------
# STEP 2: Generate IPO URL from each entry
# ----------------------------------------
def generate_ipo_url(ipo):
    base_url = "https://www.investorgain.com/ipo"
    folder = ipo.get("urlrewrite_folder_name", "")
    ipo_id = ipo.get("id", "")
    return f"{base_url}/{folder}/{ipo_id}/"

# -------------------------------------------------------
# STEP 3: Extract 'Last Updated on' date from the IPO URL
# -------------------------------------------------------
def extract_last_updated(soup):
    try:
        # Method 1: Specific <div class="row"><div class="col-12"><p>...</p></div></div>
        row_divs = soup.find_all("div", class_="row")
        for row in row_divs:
            col_div = row.find("div", class_="col-12")
            if col_div:
                p_tag = col_div.find("p")
                if p_tag and "Last Updated on" in p_tag.get_text():
                    return p_tag.get_text(strip=True).replace("Last Updated on", "").strip()

        # Method 2: Fallback - search all <p> tags
        for p in soup.find_all("p"):
            text = p.get_text(strip=True)
            if "Last Updated on" in text:
                return text.replace("Last Updated on", "").strip()

        # Method 3: Regex match as last resort
        match = re.search(r"\d{2}-[A-Za-z]{3}-\d{4} \d{2}:\d{2}:\d{2}", soup.get_text())
        if match:
            return match.group(0)

        return "Last updated info not found"
    except Exception as e:
        return f"Error: {str(e)}"

# -------------------------------------------------------
# STEP 4: Process All IPOs - build URLs & get update date
# -------------------------------------------------------
def process_ipos():
    ipo_list = fetch_all_ipos()
    result = []

    for ipo in ipo_list:
        url = generate_ipo_url(ipo)
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            last_updated = extract_last_updated(soup)

            result.append({
                "Company": ipo.get("company_short_name", ""),
                "IPO ID": ipo.get("id", ""),
                "IPO URL": url,
                "Last Updated": last_updated
            })
            print(f"✅ Processed: {ipo['company_short_name']} | Last Updated: {last_updated}")
        except Exception as e:
            print(f"❌ Error processing {url}: {e}")

    return result



# --- Save to JSON ---
def save_to_json(data, filename="last_updated_data.json"):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"\n💾 Data saved successfully to: {filename}")
    except IOError as e:
        print(f"❌ File write error: {e}")

# ----------------------------------------
# MAIN EXECUTION
# ----------------------------------------
if __name__ == "__main__":
    all_ipo_data = process_ipos()
    save_to_json(all_ipo_data)
    print("✅ All data saved to last_updated_data.json")
    
