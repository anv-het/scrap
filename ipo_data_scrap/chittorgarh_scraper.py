# chittorgarh_scraper.py

import requests
import pandas as pd
from bs4 import BeautifulSoup

def get_chittorgarh_data():
    url = "https://webnodejs.chittorgarh.com/cloud/report/data-read/82/1/6/2025/2025-26/0/all/0?search=&v=16-18"
    headers = {
        "accept": "application/json",
        "referer": "https://www.chittorgarh.com/",
        "origin": "https://www.chittorgarh.com",
        "user-agent": "Mozilla/5.0"
    }

    print("🔄 Fetching data from Chittorgarh...")
    res = requests.get(url, headers=headers)
    data = res.json()

    rows = data.get("reportTableData", [])
    print(f"✅ Fetched {len(rows)} IPOs from Chittorgarh")

    all_data = []
    for row in rows:
        soup = BeautifulSoup(row.get("Company", ""), "html.parser")
        all_data.append({
            "IPO Name": soup.text.strip(),
            "Open Date": row.get("Opening Date", ""),
            "Close Date": row.get("Closing Date", ""),
            "Listing Date": row.get("Listing Date", ""),
            "Issue Price": row.get("Issue Price (Rs.)", ""),
            "Issue Amount (Cr)": row.get("Issue Amount (Rs.cr.)", ""),
            "Listing At": row.get("Listing at", ""),
            "Lead Manager": BeautifulSoup(row.get("Lead Manager", ""), "html.parser").text.strip(),
            "Logo": row.get("~compare_image", ""),
            "URL": f"https://www.chittorgarh.com/ipo/{row.get('~URLRewrite_Folder_Name', '')}/"
        })

    return pd.DataFrame(all_data)
