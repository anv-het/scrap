import requests
from bs4 import BeautifulSoup
import json
import re

def clean_text(text):
    """Cleans extracted text by removing extra spaces, newlines, and non-breaking spaces."""
    if text:
        text = text.replace('\xa0', ' ').replace('\n', ' ').strip()
        text = re.sub(r'\s+', ' ', text)
    return text

def get_ipo_lots(soup):
    """
    Extracts IPO lots information from the soup object.
    
    Args:
        soup: BeautifulSoup object of the IPO detail page
        
    Returns:
        dict: Contains IPO lots information
    """
    ipo_lots = {}
    
    # Find the IPO Lots Table
    lots_table_header = soup.find('h2', itemprop='about', string=lambda s: s and "IPO Lots" in s)
    if lots_table_header:
        lots_table = lots_table_header.find_next_sibling('table', class_='table table-bordered table-striped table-hover w-auto')
        if lots_table:
            tbody = lots_table.find('tbody')
            if tbody:
                rows = tbody.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) == 2:
                        key = clean_text(cols[0].get_text(strip=True)).replace(':', '')
                        value = clean_text(cols[1].get_text(strip=True))
                        ipo_lots[key] = value
    
    return {"IPO Lots": ipo_lots} if ipo_lots else {"IPO Lots": {}}

def scrape_ipo_lots_from_url(url):
    """
    Scrapes IPO lots from a given URL.
    
    Args:
        url: URL of the IPO detail page
        
    Returns:
        dict: IPO lots data
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        return get_ipo_lots(soup)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching IPO lots from {url}: {e}")
        return {"IPO Lots": {}}

def save_ipo_lots_to_json(ipo_data, filename="ipo_lots.json"):
    """
    Saves IPO lots data to JSON file.
    
    Args:
        ipo_data: Dictionary containing IPO lots data
        filename: Output JSON filename
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(ipo_data, f, ensure_ascii=False, indent=2)
        print(f"IPO lots data saved to {filename}")
    except IOError as e:
        print(f"Error saving IPO lots to JSON: {e}")

if __name__ == "__main__":
    # Example usage
    test_url = "https://www.investorgain.com/ipo/globe-civil-projects-limited/3299/"
    ipo_lots_data = scrape_ipo_lots_from_url(test_url)
    save_ipo_lots_to_json(ipo_lots_data)
    print("IPO Lots Data:", json.dumps(ipo_lots_data, indent=2))