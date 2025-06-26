# # # merge_ipo_data.py
# # import pandas as pd
# # from chittorgarh_scraper import get_chittorgarh_data
# # from investorgain_scraper import get_investorgain_data

# # def clean_name(name):
# #     name = name.lower()
# #     for word in ["limited", "ipo", "ltd", "public", "company"]:
# #         name = name.replace(word, "")
# #     return name.strip()

# # # Fetch
# # ch_df = get_chittorgarh_data()
# # ig_df = get_investorgain_data()

# # # Add clean names
# # ch_df["match_key"] = ch_df["IPO Name"].apply(clean_name)
# # ig_df["match_key"] = ig_df["IPO Name"].apply(clean_name)

# # # Merge
# # print("🔗 Merging datasets...")
# # final_df = pd.merge(ch_df, ig_df, on="match_key", how="outer", suffixes=("_Chittorgarh", "_InvestorGain"))

# # # Drop match_key from final output
# # final_df.drop(columns=["match_key"], inplace=True)

# # # Show sample
# # print("\n✅ Final Combined Data Sample:\n")
# # print(final_df[["IPO Name_Chittorgarh", "IPO Name_InvestorGain", "Open Date", "Close Date", "GMP", "Issue Price", "Est. Listing"]].head())

# # # Save
# # final_df.to_csv("merged_ipo_data.csv", index=False)
# # print("\n📁 Merged data saved to 'merged_ipo_data.csv'")

# # merge_ipo_data.py

# import sqlite3
# import json
# from chittorgarh_scraper import get_chittorgarh_data
# from investorgain_scraper import get_investorgain_data

# def clean_name(name):
#     name = name.lower()
#     for word in ["limited", "ipo", "ltd", "public", "company"]:
#         name = name.replace(word, "")
#     return name.strip()

# # 1️⃣ Fetch data
# ch_df = get_chittorgarh_data()
# ig_df = get_investorgain_data()

# # 2️⃣ Clean + Merge
# ch_df["match_key"] = ch_df["IPO Name"].apply(clean_name)
# ig_df["match_key"] = ig_df["IPO Name"].apply(clean_name)
# final_df = ch_df.merge(ig_df, on="match_key", how="outer", suffixes=("_Chittorgarh", "_InvestorGain"))
# final_df.drop(columns=["match_key"], inplace=True)

# # 3️⃣ Save to CSV
# csv_path = "merged_ipo_data.csv"
# final_df.to_csv(csv_path, index=False)
# print(f"📄 CSV saved to {csv_path}")

# # 4️⃣ Save to JSON
# json_path = "merged_ipo_data.json"
# final_df.to_json(json_path, orient="records", indent=4)
# print(f"📘 JSON saved to {json_path}")

# # 5️⃣ Save to SQLite
# sqlite_path = "ipo_data.db"
# conn = sqlite3.connect(sqlite_path)
# final_df.to_sql("ipo_records", conn, if_exists="replace", index=False)
# conn.close()
# print(f"📦 Data saved to SQLite DB: {sqlite_path} (table: ipo_records)")

# # ✅ Show sample
# print("\n📌 Sample Data Preview:\n")
# print(final_df.head(3))



import requests
import pandas as pd
import time
from bs4 import BeautifulSoup

def fetch_chittorgarh_data():
    url = "https://webnodejs.chittorgarh.com/cloud/report/data-read/82/1/6/2025/2025-26/0/all/0?search=&v=17-39"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.chittorgarh.com/",
        "Origin": "https://www.chittorgarh.com",
        "Accept": "application/json"
    }
    
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    json_data = res.json()
    
    # Extract the data from reportTableData
    chittorgarh_data = json_data.get('reportTableData', [])
    
    # If the response is paginated, we could loop through pages.
    # For simplicity, we'll just pull data from the first page.
    total_pages = json_data.get('totalPages', 1)
    
    if total_pages > 1:
        for page in range(2, total_pages + 1):
            # Modify the URL to include pagination
            paginated_url = f"{url}&iPageNo={page}"
            res = requests.get(paginated_url, headers=headers)
            res.raise_for_status()
            paginated_data = res.json().get('reportTableData', [])
            chittorgarh_data.extend(paginated_data)
    
    return chittorgarh_data

def fetch_investorgain_data():
    url = "https://webnodejs.investorgain.com/cloud/report/data-read/331/1/6/2025/2025-26/0/ipo?search=&v=16-18"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.investorgain.com/",
        "Origin": "https://www.investorgain.com",
        "Accept": "application/json"
    }
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    json_data = res.json()
    
    # Extract the data from reportTableData
    investorgain_data = json_data.get('reportTableData', [])
    
    # For pagination (similar to Chittorgarh data)
    total_pages = json_data.get('totalPages', 1)
    
    if total_pages > 1:
        for page in range(2, total_pages + 1):
            # Modify the URL to include pagination
            paginated_url = f"{url}&iPageNo={page}"
            res = requests.get(paginated_url, headers=headers)
            res.raise_for_status()
            paginated_data = res.json().get('reportTableData', [])
            investorgain_data.extend(paginated_data)
    
    return investorgain_data

def extract_slug(url):
    """Extract slug like 'neetu-yoshi-ipo' from URL"""
    if not url:
        return None
    parts = url.strip("/").split("/")
    if "ipo" in parts:
        idx = parts.index("ipo")
        if idx + 1 < len(parts):
            return parts[idx + 1]
    return parts[-1]

def clean_html_tags(html_text):
    return BeautifulSoup(html_text, "html.parser").get_text() if html_text else ""

def merge_data(chittor_data, invest_data):
    chittor_df = pd.DataFrame(chittor_data)
    invest_df = pd.DataFrame(invest_data)

    # DEBUG: print chittorgarh columns to verify slug column name
    print("Chittorgarh columns:", chittor_df.columns.tolist())
    print("Investorgain columns:", invest_df.columns.tolist())

    # Get slug column safely from chittorgarh data
    if "~urlrewrite_folder_name" in chittor_df.columns:
        chittor_df["slug"] = chittor_df["~urlrewrite_folder_name"].apply(extract_slug)
    elif "~URLRewrite_Folder_Name" in chittor_df.columns:
        chittor_df["slug"] = chittor_df["~URLRewrite_Folder_Name"].apply(extract_slug)
    else:
        raise KeyError("Slug column not found in Chittorgarh data.")

    # For investorgain data slug extraction
    if "~urlrewrite_folder_name" in invest_df.columns:
        invest_df["slug"] = invest_df["~urlrewrite_folder_name"].apply(extract_slug)
    elif "~URLRewrite_Folder_Name" in invest_df.columns:
        invest_df["slug"] = invest_df["~URLRewrite_Folder_Name"].apply(extract_slug)
    else:
        # Try alternative or create slug from Name field
        invest_df["slug"] = invest_df["Name"].apply(lambda x: clean_html_tags(x).lower().replace(" ", "-") if x else None)

    # Clean company names (text only)
    if "Company" in chittor_df.columns:
        chittor_df["Company Name"] = chittor_df["Company"].apply(clean_html_tags)
    else:
        chittor_df["Company Name"] = None

    if "Name" in invest_df.columns:
        invest_df["Company Name"] = invest_df["Name"].apply(clean_html_tags)
    else:
        invest_df["Company Name"] = None

    # Merge on slug (outer join to keep all IPOs)
    merged_df = pd.merge(chittor_df, invest_df, on="slug", how="outer", suffixes=("_chittor", "_invest"))

    return merged_df

def main():
    print("Fetching data from Chittorgarh...")
    chittor_data = fetch_chittorgarh_data()
    time.sleep(1)

    print("Fetching data from Investorgain...")
    invest_data = fetch_investorgain_data()

    print("Merging data...")
    merged_df = merge_data(chittor_data, invest_data)

    print("Saving merged IPO data to 'ipo_merged_data.csv'")
    merged_df.to_csv("ipo_merged_data.csv", index=False)
    print("✅ Done.")

if __name__ == "__main__":
    main()
