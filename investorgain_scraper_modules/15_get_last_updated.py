import requests
from bs4 import BeautifulSoup

def extract_last_updated(soup):
    try:
        # Method 1: Primary method (most likely structure)
        row_divs = soup.find_all("div", class_="row")
        for row in row_divs:
            col_div = row.find("div", class_="col-12")
            if col_div:
                p_tag = col_div.find("p")
                if p_tag and "Last Updated on" in p_tag.get_text():
                    return p_tag.get_text(strip=True).replace("Last Updated on", "").strip()

        # Method 2: Fallback search anywhere in <p> tags
        for p in soup.find_all("p"):
            text = p.get_text(strip=True)
            if "Last Updated on" in text:
                return text.replace("Last Updated on", "").strip()

        # Method 3: Last fallback, look for exact datetime format
        import re
        match = re.search(r"\d{2}-[A-Za-z]{3}-\d{4} \d{2}:\d{2}:\d{2}", soup.get_text())
        if match:
            return match.group(0)

        return "Last updated info not found"
    except Exception as e:
        return f"Error: {str(e)}"

# Example usage
if __name__ == "__main__":
    url = 'https://www.investorgain.com/ipo/indogulf-cropsciences/1277/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    last_updated = extract_last_updated(soup)
    print(f"📅 Last Updated Date: {last_updated}")
