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

def get_ipo_gmp(soup):
    """
    Extracts IPO GMP (Grey Market Premium) information from the soup object.
    
    Args:
        soup: BeautifulSoup object of the IPO detail page
        
    Returns:
        dict: Contains IPO GMP information as list
    """
    gmp_data = []
    
    # Find the IPO GMP Table
    gmp_table_header = soup.find('h2', itemprop='about', string=lambda s: s and ('IPO GMP' in s or 'Live GMP' in s))
    if not gmp_table_header:
        gmp_table_header = soup.find('h3', itemprop='about', string=lambda s: s and ('IPO GMP' in s or 'Live GMP' in s))

    if gmp_table_header:
        gmp_table = gmp_table_header.find_next_sibling('table', class_='table table-bordered table-striped w-auto')
        if gmp_table:
            thead = gmp_table.find('thead')
            tbody = gmp_table.find('tbody')
            
            if thead and tbody:
                headers = [clean_text(th.get_text(strip=True)) for th in thead.find_all('th')]
                rows = tbody.find_all('tr')
                
                for row in rows:
                    cols = row.find_all('td')
                    gmp_entry = {}
                    for i, col in enumerate(cols):
                        if i < len(headers):
                            gmp_entry[headers[i]] = clean_text(col.get_text(strip=True))
                    if gmp_entry:
                        gmp_data.append(gmp_entry)
    
    return {"IPO GMP": gmp_data} if gmp_data else {"IPO GMP": []}

def scrape_ipo_gmp_from_url(url):
    """
    Scrapes IPO GMP from a given URL.
    
    Args:
        url: URL of the IPO detail page
        
    Returns:
        dict: IPO GMP data
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        return get_ipo_gmp(soup)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching IPO GMP from {url}: {e}")
        return {"IPO GMP": []}

def save_ipo_gmp_to_json(ipo_data, filename="ipo_gmp.json"):
    """
    Saves IPO GMP data to JSON file.
    
    Args:
        ipo_data: Dictionary containing IPO GMP data
        filename: Output JSON filename
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(ipo_data, f, ensure_ascii=False, indent=2)
        print(f"IPO GMP data saved to {filename}")
    except IOError as e:
        print(f"Error saving IPO GMP to JSON: {e}")

if __name__ == "__main__":
    # Example usage
    test_url = "https://www.investorgain.com/ipo/globe-civil-projects-limited/3299/"
    ipo_gmp_data = scrape_ipo_gmp_from_url(test_url)
    save_ipo_gmp_to_json(ipo_gmp_data)
    print("IPO GMP Data:", json.dumps(ipo_gmp_data, indent=2))