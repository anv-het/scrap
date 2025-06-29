import requests
from bs4 import BeautifulSoup
import json
import time
import re
from datetime import datetime

def fetch_ipo_list_from_api():
    """
    Fetches the list of IPOs from the Investorgain API.
    This function is reused for the initial list.
    """
    api_url = "https://webnodejs.investorgain.com/cloud/ipo/list-read"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        if data.get("msg") == 1 and "ipoList" in data:
            return data["ipoList"]
        else:
            print(f"API response not as expected: {data}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Error fetching IPO list from API: {e}")
        return []

def clean_text(text):
    """
    Cleans extracted text by removing extra spaces, newlines, and non-breaking spaces.
    Handles HTML entities automatically if BeautifulSoup has already parsed them.
    """
    if text:
        text = text.replace('\xa0', ' ').replace('\n', ' ').strip()
        text = re.sub(r'\s+', ' ', text)
    return text


def extract_company_about(soup):
    """
    Extracts the full company name and the 'About Company' paragraph(s) from the soup object.
    Now correctly handles cases where paragraphs are nested within a div immediately after the h3.
    """
    company_full_name = "N/A"
    about_company_text = "N/A"

    print("DEBUG: Starting extract_company_about function")

    # Find the <h3> tag with itemprop="about"
    about_h3 = soup.find('h3', itemprop="about")
    print(f"DEBUG: Found <h3> tag with itemprop='about': {about_h3}")

    if about_h3:
        h3_text = clean_text(about_h3.get_text())
        print(f"DEBUG: Cleaned text from <h3> tag: {h3_text}")

        # Extract "Company Full Name" from the h3 tag's text
        match = re.search(r'About Company\s*-\s*(.+)', h3_text, re.IGNORECASE)
        if match:
            company_full_name = clean_text(match.group(1))
            print(f"DEBUG: Extracted company full name: {company_full_name}")
        else:
            print(f"DEBUG: Could not parse full company name from H3: {h3_text}")

        # MODIFIED LOGIC FOR PARAGRAPHS: Find the <div> immediately after the <h3>
        about_content_container = None
        current_sibling = about_h3.next_sibling
        while current_sibling:
            if isinstance(current_sibling, str): # Skip NavigableString (whitespace, newlines)
                current_sibling = current_sibling.next_sibling
                continue

            if current_sibling.name == 'div':
                about_content_container = current_sibling
                print("DEBUG: Found direct sibling <div> container for about text.")
                break # Found the container, exit loop
            else: # If it's not a div and not just whitespace, it's not the expected container.
                print(f"DEBUG: Next sibling is '{current_sibling.name}', not the expected <div> container. Stopping search for container.")
                break # Stop if we encounter an unexpected tag
            
            current_sibling = current_sibling.next_sibling


        if about_content_container:
            # Now, find all <p> tags *within* this specific div
            about_paragraphs = []
            paragraphs_in_div = about_content_container.find_all('p')
            
            print(f"DEBUG: Found {len(paragraphs_in_div)} <p> tags within the container div.")

            for p_tag in paragraphs_in_div:
                paragraph_text = clean_text(p_tag.get_text())
                if paragraph_text: # Only add if not empty after cleaning
                    about_paragraphs.append(paragraph_text)
                    print(f"DEBUG: Added paragraph: {paragraph_text[:50]}...") # Print snippet for long text
            
            if about_paragraphs:
                about_company_text = "\n\n".join(about_paragraphs) # Join paragraphs with double newline
                print(f"DEBUG: About Company Text (final): {about_company_text[:100]}...") # Print snippet
            else:
                print("DEBUG: No about company paragraphs found within the container div.")
        else:
            print("DEBUG: No 'About Company' content <div> container found after <h3> tag.")
    else:
        print("DEBUG: No <h3> tag with itemprop='about' found.")


    return {
        'Company Full Name (Scraped)': company_full_name,
        'About Company Text': about_company_text
    }






