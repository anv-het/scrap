import requests
from bs4 import BeautifulSoup
import json

# 🚀 Fetch live HTML
print("🌐 Fetching page content...")
url = "https://ipowatch.in/ipo-grey-market-premium-latest-ipo-gmp/"
resp = requests.get(url, headers={
    "User-Agent": "Mozilla/5.0"
})
resp.raise_for_status()
print("✅ Page fetched!")

# 🧠 Parse HTML
soup = BeautifulSoup(resp.text, "lxml")

# 🔍 Locate all tables (filter to relevant ones)
tables = soup.find_all("table")
print(f"🔍 Found {len(tables)} table(s).")

def parse_table(tbl, idx):
    print(f"📊 Parsing table #{idx}...")
    rows = tbl.find_all("tr")
    if not rows:
        print("⚠️ No rows found — skipping.")
        return None

    # Determine headers
    header_cells = rows[0].find_all(["td", "th"])
    headers = [cell.get_text(strip=True).replace("\n", " ") for cell in header_cells]
    print(f"🧾 Headers: {headers}")

    data = []
    for ridx, row in enumerate(rows[1:], start=1):
        cols = row.find_all("td")
        if not cols:
            continue
        row_dict = {}
        for col_i, col in enumerate(cols):
            text = col.get_text(strip=True)
            # If first column has a link
            if col_i == 0:
                a = col.find("a")
                row_dict[headers[col_i]] = a.text.strip() if a else text
                row_dict[headers[col_i] + "__link"] = a["href"] if a else None
            else:
                row_dict[headers[col_i]] = text.replace("₹", "Rs. ")
        print(f"✅ Row {ridx} parsed.")
        data.append(row_dict)

    return {"headers": headers, "rows": data}

# 🚧 Process each table
all_tables = []
for i, tbl in enumerate(tables, start=1):
    result = parse_table(tbl, i)
    if result and result["rows"]:
        all_tables.append({"table_id": i, **result})

# 💾 Save JSON output
for table in all_tables:
    filename = f"ipo_table_{table['table_id']}.json"
    print(f"💾 Saving JSON: {filename}")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump({"headers": table["headers"], "data": table["rows"]}, f, indent=4, ensure_ascii=False)
print(f"🎉 Completed! {len(all_tables)} table(s) saved.")

# 👀 Quick preview
for table in all_tables:
    print(f"\n--- Table #{table['table_id']} preview ---")
    for row in table["rows"][:3]:
        print(row)
