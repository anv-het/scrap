import requests
import json
import os
import sys
from typing import Optional

COOKIES_FILE = 'nse_cookies.json'
BASE_URL = 'https://www.nseindia.com/api/quote-equity?symbol='
OUTPUT_FILE = 'stock_details.json'

def load_cookies() -> Optional[dict]:
    try:
        with open(COOKIES_FILE, 'r') as f:
            cookies = json.load(f)
        print('🍪 Cookies loaded successfully')
        return cookies
    except FileNotFoundError:
        print(f'❌ Cookie file not found: {COOKIES_FILE}')
    except json.JSONDecodeError:
        print(f'❌ Invalid JSON format in cookie file.')
    return None

def fetch_stock_details(symbol: str, cookies: dict) -> Optional[dict]:
    url = f"{BASE_URL}{symbol.upper()}"
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept': '*/*',
        'Referer': 'https://www.nseindia.com/'
    }

    session = requests.Session()
    for name, value in cookies.items():
        session.cookies.set(name, value)

    try:
        response = session.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        print(f'✅ Fetched data for {symbol}')
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f'❌ Failed to fetch {symbol}: {e}')
        return None

def save_all_to_json(data: dict):
    try:
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        print(f'💾 Saved all data to {OUTPUT_FILE}')
    except Exception as e:
        print(f'❌ Failed to save to {OUTPUT_FILE}: {e}')

def main():
    if len(sys.argv) < 2:
        print("⚠️ Usage: python get_stock_details.py SYMBOL1 [SYMBOL2 SYMBOL3 ...]")
        return

    symbols = sys.argv[1:]
    cookies = load_cookies()
    if not cookies:
        return

    all_data = {}

    for symbol in symbols:
        print(f"\n🔍 Processing {symbol}...")
        data = fetch_stock_details(symbol, cookies)
        if data:
            all_data[symbol.upper()] = data
        else:
            all_data[symbol.upper()] = {"error": "Failed to fetch data"}

    save_all_to_json(all_data)

if __name__ == '__main__':
    main()
