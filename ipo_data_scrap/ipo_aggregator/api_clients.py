# api_clients.py - Refined for Auto Decompression and Error Handling

import requests
import json
# Removed brotli, gzip, zlib, io imports as we'll rely on requests' automatic decompression

from config import CHITTORGARH_BASE_URL, INVESTORGAIN_BASE_URL, MONEYCONTROL_CALENDAR_URL, CHITTORGARH_HEADERS, INVESTORGAIN_HEADERS, COMMON_HEADERS
from utils import parse_flexible_date

def fetch_json_data(url, headers):
    """
    Generic function to fetch JSON data from a given URL with specified headers.
    Relies on requests' automatic content decompression and includes robust error handling.
    
    Args:
        url (str): The URL to fetch data from.
        headers (dict): A dictionary of HTTP headers to send with the request.
        
    Returns:
        dict or None: Parsed JSON data if successful, None otherwise.
    """
    print(f"Attempting to fetch data from: {url}")
    try:
        # requests automatically handles content decompression (gzip, deflate, brotli)
        # if the 'Accept-Encoding' header is set appropriately in config.py
        response = requests.get(url, headers=headers, timeout=20) # Increased timeout to 20 seconds
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        
        # --- DEBUGGING PRINTS ---
        print(f"  Response Status Code: {response.status_code}")
        print(f"  Response Headers: {response.headers}")
        print(f"  Response Encoding (from headers): {response.encoding}") # Show detected encoding
        
        # Try to decode to text, then parse JSON
        try:
            # response.text attempts to decode content using detected encoding or UTF-8 fallback
            decoded_content = response.text
            print(f"  Decoded Content (first 500 chars): {decoded_content[:500]}...")
            
            json_data = json.loads(decoded_content)
            print(f"  Successfully parsed JSON. Type: {type(json_data)}")
            return json_data
        except json.JSONDecodeError as jde:
            print(f"  Failed to decode JSON from response for {url}: {jde}")
            print(f"  Full Decoded Content (for JSONDecodeError): {decoded_content}")
            # If JSON decoding fails, it's likely not JSON. Return None.
            return None
        except UnicodeDecodeError as ude:
            print(f"  UnicodeDecodeError during text decoding for {url}: {ude}")
            print(f"  Raw response content (first 500 bytes): {response.content[:500]}")
            return None # Return None if text decoding fails

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error fetching {url}: {e}")
    except requests.exceptions.ConnectionError as e:
        print(f"Connection Error fetching {url}: {e}")
    except requests.exceptions.Timeout as e:
        print(f"Timeout Error fetching {url}: {e}")
    except requests.exceptions.RequestException as e:
        print(f"An unexpected requests error occurred fetching {url}: {e}")
    except Exception as e: # Catch any other unexpected errors during the process
        print(f"An unhandled general error occurred in fetch_json_data for {url}: {e}")
    return None

def get_chittorgarh_ipos(ipo_type, month, year, financial_year):
    """
    Fetches basic IPO details from Chittorgarh.
    
    Args:
        ipo_type (str): 'mainboard', 'sme', or 'all'.
        month (int): Current month (e.g., 6 for June).
        year (int): Current year (e.g., 2025).
        financial_year (str): Financial year string (e.g., '2025-26').
        
    Returns:
        list: List of IPO dictionaries, or empty list if data fetching fails.
    """
    # Removed the 'v' parameter as it might be dynamic or causing issues
    url = f"{CHITTORGARH_BASE_URL}/82/1/{month}/{year}/{financial_year}/0/{ipo_type}/0?search="
    data = fetch_json_data(url, CHITTORGARH_HEADERS)
    # Ensure data is a dictionary before using .get
    return data.get("reportTableData", []) if isinstance(data, dict) else []

def get_chittorgarh_mainboard_subscription(month, year, financial_year):
    """
    Fetches Mainboard IPO subscription status from Chittorgarh.
    
    Args:
        month (int): Current month.
        year (int): Current year.
        financial_year (str): Financial year string.
        
    Returns:
        list: List of subscription dictionaries.
    """
    # Removed the 'v' parameter
    url = f"{CHITTORGARH_BASE_URL}/21/1/{month}/{year}/{financial_year}/0/0/0?search="
    data = fetch_json_data(url, CHITTORGARH_HEADERS)
    return data.get("reportTableData", []) if isinstance(data, dict) else []

def get_chittorgarh_sme_subscription(month, year, financial_year):
    """
    Fetches SME IPO subscription status from Chittorgarh.
    
    Args:
        month (int): Current month.
        year (int): Current year.
        financial_year (str): Financial year string.
        
    Returns:
        list: List of subscription dictionaries.
    """
    # Removed the 'v' parameter
    url = f"{CHITTORGARH_BASE_URL}/22/1/{month}/{year}/{financial_year}/0/0/0?search="
    data = fetch_json_data(url, CHITTORGARH_HEADERS)
    return data.get("reportTableData", []) if isinstance(data, dict) else []

def get_investorgain_all_gmp(month, year, financial_year):
    """
    Fetches All IPO GMP details from Investorgain.
    
    Args:
        month (int): Current month.
        year (int): Current year.
        financial_year (str): Financial year string.
        
    Returns:
        list: List of GMP dictionaries.
    """
    # Removed the 'v' parameter
    url = f"{INVESTORGAIN_BASE_URL}/331/1/{month}/{year}/{financial_year}/0/all?search="
    data = fetch_json_data(url, INVESTORGAIN_HEADERS)
    return data.get("reportTableData", []) if isinstance(data, dict) else []

def get_investorgain_live_subscription(month, year, financial_year):
    """
    Fetches Live IPO Subscription Report from Investorgain.
    
    Args:
        month (int): Current month.
        year (int): Current year.
        financial_year (str): Financial Year string.
        
    Returns:
        list: List of subscription dictionaries.
    """
    # Removed the 'v' parameter
    url = f"{INVESTORGAIN_BASE_URL}/333/1/{month}/{year}/{financial_year}/0/all?search="
    data = fetch_json_data(url, INVESTORGAIN_HEADERS)
    return data.get("reportTableData", []) if isinstance(data, dict) else []

def get_moneycontrol_ipo_calendar():
    """
    Fetches IPO Calendar data from Moneycontrol.
    
    Returns:
        list: List of IPO calendar dictionaries.
    """
    url = MONEYCONTROL_CALENDAR_URL
    data = fetch_json_data(url, COMMON_HEADERS)
    
    # --- ADDITIONAL DEBUGGING PRINTS ---
    print(f"  get_moneycontrol_ipo_calendar received data from fetch_json_data: {data}")
    print(f"  Type of data received by get_moneycontrol_ipo_calendar: {type(data)}")
    if isinstance(data, dict):
        print(f"  Type of data.get('data', []) for Moneycontrol: {type(data.get('data', []))}")
    # --- END ADDITIONAL DEBUGGING PRINTS ---

    return data.get("data", []) if isinstance(data, dict) else []

