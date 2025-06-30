import requests
from bs4 import BeautifulSoup
import re
import json

# ----------------------------------
# 1. Fetch All IPOs from API
# ----------------------------------
def fetch_all_ipos():
    url = "https://webnodejs.investorgain.com/cloud/ipo/list-read"
    try:
        response = requests.get(url)
        data = response.json()
        if data.get("msg") == 1 and "ipoList" in data:
            return data["ipoList"]
        return []
    except Exception as e:
        print(f"Error fetching IPO list: {e}")
        return []

# ----------------------------------
# 2. Generate URL for an IPO
# ----------------------------------
def generate_ipo_url(ipo):
    base_url = "https://www.investorgain.com/ipo"
    folder = ipo.get("urlrewrite_folder_name", "")
    ipo_id = ipo.get("id", "")
    return f"{base_url}/{folder}/{ipo_id}/"

# ----------------------------------
# 3. Extract "Last Updated on" Date
# ----------------------------------
def extract_last_updated(soup):
    try:
        row_divs = soup.find_all("div", class_="row")
        for row in row_divs:
            col_div = row.find("div", class_="col-12")
            if col_div:
                p_tag = col_div.find("p")
                if p_tag and "Last Updated on" in p_tag.get_text():
                    return p_tag.get_text(strip=True).replace("Last Updated on", "").strip()

        for p in soup.find_all("p"):
            text = p.get_text(strip=True)
            if "Last Updated on" in text:
                return text.replace("Last Updated on", "").strip()

        match = re.search(r"\d{2}-[A-Za-z]{3}-\d{4} \d{2}:\d{2}:\d{2}", soup.get_text())
        if match:
            return match.group(0)

        return "Last updated info not found"
    except Exception as e:
        return f"Error: {str(e)}"

# ----------------------------------
# 4. Extract Company Address or Registrar
# ----------------------------------
def extract_company_address(card):
    result = {
        "name": "",
        "address": "",
        "website": "",
        "phone": "",
        "email": ""
    }
    try:
        body = card.find("div", class_="card-body")
        children = list(body.children)

        name = None
        for i, child in enumerate(children):
            if getattr(child, "name", None) == "strong":
                name = child.get_text(strip=True)
                start_index = i + 1
                break
        if not name:
            return result
        result["name"] = name

        address_parts = []
        for child in children[start_index:]:
            if getattr(child, "name", None) == "strong":
                break
            text = child if isinstance(child, str) else child.get_text(strip=True)
            text = text.strip()
            if text:
                address_parts.append(text)

        result["address"] = ', '.join(address_parts).replace(",,", ",")

        strongs_after = [c for c in children if getattr(c, "name", None) == "strong"][1:]

        for strong_tag in strongs_after:
            label = strong_tag.get_text(strip=True).lower()
            next_node = strong_tag.next_sibling
            while next_node and (isinstance(next_node, str) and not next_node.strip()):
                next_node = next_node.next_sibling

            value = next_node.get_text(strip=True) if hasattr(next_node, "get_text") else (next_node or "").strip()

            if "website" in label:
                result["website"] = value
            elif "phone" in label:
                result["phone"] = value
            elif "email" in label:
                result["email"] = value
    except Exception as e:
        result["error"] = str(e)
    return result

# ----------------------------------
# 5. Extract Lead Managers
# ----------------------------------
def extract_ipo_lead_manager(card):
    try:
        body = card.find("div", class_="card-body")
        ol = body.find("ol")
        return [li.get_text(strip=True) for li in ol.find_all("li")] if ol else []
    except Exception as e:
        return [f"Error: {str(e)}"]

# ----------------------------------
# 6. Parse Contact Sections
# ----------------------------------
def extract_contact_sections(soup):
    data = {
        "company_address": {},
        "ipo_registrar": {},
        "ipo_lead_manager": []
    }

    cards = soup.find_all("div", class_="card")
    for card in cards:
        h3 = card.find("h3")
        if not h3:
            continue
        heading = h3.get_text(strip=True)

        if "Company Address" in heading:
            data["company_address"] = extract_company_address(card)
        elif "Registrar" in heading:
            data["ipo_registrar"] = extract_company_address(card)
        elif "Lead Manager" in heading:
            data["ipo_lead_manager"] = extract_ipo_lead_manager(card)

    return data

# ----------------------------------
# 7. Process All IPOs
# ----------------------------------
def process_all_ipos():
    all_ipos = fetch_all_ipos()
    results = []

    for ipo in all_ipos:
        ipo_url = generate_ipo_url(ipo)
        try:
            res = requests.get(ipo_url)
            soup = BeautifulSoup(res.text, "html.parser")

            last_updated = extract_last_updated(soup)
            contact_details = extract_contact_sections(soup)

            final_data = {
                "company_name": ipo.get("company_short_name", ""),
                "ipo_id": ipo.get("id"),
                "ipo_url": ipo_url,
                "last_updated": last_updated,
                "company_address": contact_details["company_address"],
                "ipo_registrar": contact_details["ipo_registrar"],
                "ipo_lead_manager": contact_details["ipo_lead_manager"]
            }

            print(f"✅ Scraped: {final_data['company_name']} | Last Updated: {last_updated}")
            results.append(final_data)
        except Exception as e:
            print(f"❌ Error scraping {ipo_url}: {e}")

    return results

# ----------------------------------
# 8. Run and Save JSON
# ----------------------------------
if __name__ == "__main__":
    all_data = process_all_ipos()

    with open("ipo_contact_data.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)

    print("\n📁 All IPO contact data saved to: ipo_contact_data.json")
