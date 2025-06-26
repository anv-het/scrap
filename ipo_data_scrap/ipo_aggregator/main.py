# main.py
# This script orchestrates the fetching, processing, and unification of IPO data from various sources.

import pandas as pd
from datetime import datetime
from api_clients import (
    get_chittorgarh_ipos, get_chittorgarh_mainboard_subscription, 
    get_chittorgarh_sme_subscription, get_investorgain_all_gmp, 
    get_investorgain_live_subscription, get_moneycontrol_ipo_calendar
)
from data_processors import unify_ipo_data
from utils import parse_flexible_date # clean_chittorgarh_company_name, clean_investorgain_company_name # These are called internally by data_processors now

def main():
    """
    Main function to fetch, process, and display unified IPO data.
    """
    print("Starting IPO data aggregation...")

    # Define the current year and month for API calls.
    # The APIs provided use 2025/2025-26 as hardcoded values,
    # so we'll simulate that or dynamically set it for actual current data.
    current_year = 2025 # Changed from datetime.now().year for testing with your example URLs
    current_month = 6   # Changed from datetime.now().month for testing with your example URLs
    financial_year = f"{current_year}-{str(current_year + 1)[2:]}" # e.g., 2025-26

    # --- Fetch Data from Chittorgarh ---
    print("\nFetching data from Chittorgarh...")
    chittorgarh_all_ipos = get_chittorgarh_ipos(
        ipo_type='all', month=current_month, year=current_year, financial_year=financial_year
    )
    chittorgarh_mainboard_subscription = get_chittorgarh_mainboard_subscription(
        month=current_month, year=current_year, financial_year=financial_year
    )
    chittorgarh_sme_subscription = get_chittorgarh_sme_subscription(
        month=current_month, year=current_year, financial_year=financial_year
    )

    # --- Fetch Data from Investorgain ---
    print("Fetching data from Investorgain...")
    investorgain_all_gmp = get_investorgain_all_gmp(
        month=current_month, year=current_year, financial_year=financial_year
    )
    investorgain_live_subscription = get_investorgain_live_subscription(
        month=current_month, year=current_year, financial_year=financial_year
    )

    # --- Fetch Data from Moneycontrol ---
    print("Fetching data from Moneycontrol...")
    moneycontrol_calendar = get_moneycontrol_ipo_calendar()

    # --- Unify Data ---
    print("\nUnifying collected data...")
    unified_data = unify_ipo_data(
        chittorgarh_all_ipos,
        chittorgarh_mainboard_subscription,
        chittorgarh_sme_subscription,
        investorgain_all_gmp,
        investorgain_live_subscription,
        moneycontrol_calendar
    )

    # Convert to DataFrame for better presentation
    df = pd.DataFrame(unified_data.values())

    # Sort the DataFrame by Opening Date for better readability
    if 'opening_date' in df.columns:
        df['opening_date_sort'] = df['opening_date'].apply(
            lambda x: parse_flexible_date(x) if pd.notna(x) else datetime.min
        )
        df = df.sort_values(by='opening_date_sort', ascending=True).drop(columns='opening_date_sort')

    print("\n--- Unified IPO Data ---")
    if not df.empty:
        print(df.to_string()) # Use to_string() to display full DataFrame without truncation
    else:
        print("No data found or unified DataFrame is empty.")

    # Optional: Save to CSV
    df.to_csv("unified_ipo_data.csv", index=False)
    print("\nUnified IPO data saved to unified_ipo_data.csv")

if __name__ == "__main__":
    main()
