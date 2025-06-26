# utils.py - UNCHANGED from previous update
# Utility functions for data processing and cleaning

from datetime import datetime
from dateutil import parser
from bs4 import BeautifulSoup

def parse_flexible_date(date_string):
    """
    Parses a date string into a datetime object using dateutil.parser.
    Handles various formats automatically.
    
    Args:
        date_string (str): The date string to parse.
        
    Returns:
        datetime: A datetime object, or None if parsing fails.
    """
    if not isinstance(date_string, str) or not date_string.strip():
        return None
    try:
        # dateutil.parser.parse is robust for various formats
        return parser.parse(date_string)
    except (parser.ParserError, TypeError, ValueError):
        # Handle cases where parsing might fail, e.g., empty string or invalid format
        return None

def clean_html_from_string(html_string):
    """
    Removes HTML tags from a string using BeautifulSoup.

    Args:
        html_string (str): The string potentially containing HTML.

    Returns:
        str: The cleaned string with HTML tags removed.
    """
    if not isinstance(html_string, str):
        return ""
    soup = BeautifulSoup(html_string, 'lxml') # Using lxml parser for speed
    return soup.get_text(separator=" ", strip=True)

def normalize_company_name(name):
    """
    Normalizes a company name for consistent comparison.
    Removes common suffixes, converts to lowercase, and strips extra spaces.
    
    Args:
        name (str): The raw company name.
        
    Returns:
        str: The normalized company name.
    """
    if not isinstance(name, str):
        return ""
    name = clean_html_from_string(name)
    name = name.lower()
    # Remove common suffixes and extra spaces
    suffixes = [" limited ipo", " ltd ipo", " ipo", " fashions", " trading ltd", " bse sme", " nse sme", " limited"]
    for suffix in suffixes:
        if name.endswith(suffix):
            name = name[:-len(suffix)]
            break # Assume only one suffix removed per run
    
    # Replace common symbols or words that might vary with consistent ones
    name = name.replace("&amp;", "&").replace(" and ", " & ")
    
    return name.strip()

# Specific cleaning functions for API responses (these now just call normalize_company_name)
def clean_chittorgarh_company_name(name_html):
    """Cleans company name from Chittorgarh, removing HTML and normalizing."""
    return normalize_company_name(name_html)

def clean_investorgain_company_name(name_html):
    """Cleans company name from Investorgain, removing HTML and normalizing."""
    return normalize_company_name(name_html)