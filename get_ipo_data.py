# *-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*#
# Fatche data from chittorgarh.com
# *-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*#

# import requests
# import pandas as pd
# from bs4 import BeautifulSoup

# # ✅ Working URL with valid parameters
# url = "https://webnodejs.chittorgarh.com/cloud/report/data-read/82/1/6/2025/2025-26/0/all/0?search=&v=16-05"

# # Add browser-like headers to prevent blocking
# headers = {
#     "User-Agent": "Mozilla/5.0",
#     "Referer": "https://www.chittorgarh.com/",
#     "Accept": "application/json"
# }

# # Fetch the data
# response = requests.get(url, headers=headers)
# print("Status Code:", response.status_code)

# try:
#     data = response.json()
    
#     # Check for the key where data is stored
#     ipo_data = data.get("reportTableData", [])
#     print(f"Total IPO entries found: {len(ipo_data)}")

#     # Clean HTML fields
#     cleaned_data = []
#     for item in ipo_data:
#         clean_item = {}
#         for key, value in item.items():
#             # If value contains HTML, clean it
#             if isinstance(value, str) and ("<a" in value or "<img" in value):
#                 clean_item[key] = BeautifulSoup(value, "html.parser").get_text(strip=True)
#             else:
#                 clean_item[key] = value
#         cleaned_data.append(clean_item)

#     # Convert to DataFrame
#     df = pd.DataFrame(cleaned_data)
    
#     # Show sample
#     print("\n🔍 Sample IPO entries:")
#     print(df.head(3))

#     # Save to CSV
#     df.to_csv("ipo_current_list.csv", index=False)
#     print("✅ Saved to: ipo_current_list.csv")

# except Exception as e:
#     print("❌ Failed to parse JSON or extract data:", e)

# if len(df) == data['totalRecords']:
#     print("✅ All records fetched")
# else:
#     print("⚠️ Missing records:", data['totalRecords'] - len(df))
# print("\n✅ Done")






# *-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*#
# Fatche data from investorgain

import requests
import pandas as pd
from bs4 import BeautifulSoup

# API URL
url = "https://webnodejs.investorgain.com/cloud/report/data-read/331/1/6/2025/2025-26/0/ipo?search=&v=16-18"

# Headers
headers = {
    "accept": "application/json, text/plain, */*",
    "origin": "https://www.investorgain.com",
    "referer": "https://www.investorgain.com/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
}

# Request
response = requests.get(url, headers=headers)
print(f"Status Code: {response.status_code}")

data = response.json()

# Debug Print
print("Top-level keys:", data.keys())

# Extract IPO data
ipo_data = data.get("reportTableData", [])

# Clean and collect
ipo_list = []
for item in ipo_data:
    name = BeautifulSoup(item.get("Name", ""), "html.parser").text.strip()
    gmp = BeautifulSoup(item.get("GMP", ""), "html.parser").text.strip()
    est_listing = BeautifulSoup(item.get("Est Listing", ""), "html.parser").text.strip()
    fire = BeautifulSoup(item.get("Fire Rating", ""), "html.parser").text.strip()
    
    ipo_list.append({
        "IPO Name": name,
        "GMP": gmp,
        "Est. Listing Price": est_listing,
        "Fire Rating": fire,
        "Price": item.get("Price", ""),
        "IPO Size": BeautifulSoup(item.get("IPO Size", ""), "html.parser").text.strip(),
        "Lot": item.get("Lot", ""),
        "P/E": item.get("~P/E", ""),
        "Open": item.get("Open", ""),
        "Close": item.get("Close", ""),
        "BoA Date": item.get("BoA Dt", ""),
        "Listing": item.get("Listing", ""),
        "GMP Updated": item.get("GMP Updated", ""),
    })

# Create DataFrame
df = pd.DataFrame(ipo_list)

# Show first few rows
print(df.head())

# Optional: Save to CSV
df.to_csv("ipo_gmp_data.csv", index=False)
print("✅ Data saved to ipo_gmp_data.csv")


