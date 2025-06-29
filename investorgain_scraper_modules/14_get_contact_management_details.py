import requests
from bs4 import BeautifulSoup
import json


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

        # Find first strong (name)
        name = None
        for i, child in enumerate(children):
            if getattr(child, "name", None) == "strong":
                name = child.get_text(strip=True)
                start_index = i + 1
                break
        if not name:
            return result
        result["name"] = name

        # Collect address parts until next <strong>
        address_parts = []
        for child in children[start_index:]:
            if getattr(child, "name", None) == "strong":
                break
            text = ''
            if isinstance(child, str):
                text = child.strip()
            else:
                text = child.get_text(strip=True)
            if text:
                address_parts.append(text)

        result["address"] = ', '.join(address_parts).replace(",,", ",")

        # Now parse labels after address (Website, Phone, Email)
        # Find all strong tags after address
        strongs_after = [c for c in children if getattr(c, "name", None) == "strong"][1:]  # exclude first

        for strong_tag in strongs_after:
            label = strong_tag.get_text(strip=True).lower()
            # The value is usually the next sibling text node or tag
            next_node = strong_tag.next_sibling
            while next_node and (isinstance(next_node, str) and not next_node.strip()):
                next_node = next_node.next_sibling
            value = ''
            if next_node:
                if isinstance(next_node, str):
                    value = next_node.strip()
                else:
                    value = next_node.get_text(strip=True)

            if "website" in label:
                result["website"] = value
            elif "phone" in label:
                result["phone"] = value
            elif "email" in label:
                result["email"] = value

    except Exception as e:
        result["error"] = str(e)

    return result

def extract_ipo_registrar(card):
    return extract_company_address(card)  # same structure


def extract_ipo_lead_manager(card):
    try:
        body = card.find("div", class_="card-body")
        ol = body.find("ol")
        return [li.get_text(strip=True) for li in ol.find_all("li")] if ol else []
    except Exception as e:
        return [f"Error: {str(e)}"]


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
            data["ipo_registrar"] = extract_ipo_registrar(card)
        elif "Lead Manager" in heading:
            data["ipo_lead_manager"] = extract_ipo_lead_manager(card)

    return data


# ---- Scraping Start ----
response = requests.get('https://www.investorgain.com/ipo/indogulf-cropsciences/1299/')
soup = BeautifulSoup(response.text, 'html.parser')

result = extract_contact_sections(soup)

print(json.dumps(result, indent=2, ensure_ascii=False))
