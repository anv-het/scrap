# # data_processors.py - UPDATED with defensive checks
# # Functions for cleaning, normalizing, and unifying IPO data.

# from collections import defaultdict
# import datetime
# from utils import normalize_company_name, parse_flexible_date

# def unify_ipo_data(
#     chittorgarh_all_ipos, 
#     chittorgarh_mainboard_subscription, 
#     chittorgarh_sme_subscription, 
#     investorgain_all_gmp, 
#     investorgain_live_subscription, 
#     moneycontrol_calendar
# ):
#     """
#     Unifies IPO data from various sources into a single structured format.
    
#     Args:
#         chittorgarh_all_ipos (list): Basic IPO data from Chittorgarh (all types).
#         chittorgarh_mainboard_subscription (list): Mainboard subscription data from Chittorgarh.
#         chittorgarh_sme_subscription (list): SME subscription data from Chittorgarh.
#         investorgain_all_gmp (list): All GMP data from Investorgain.
#         investorgain_live_subscription (list): Live subscription data from Investorgain.
#         moneycontrol_calendar (list): IPO calendar data from Moneycontrol.
        
#     Returns:
#         dict: A dictionary where keys are unique IPO identifiers (normalized name + open date)
#               and values are dictionaries of unified IPO data.
#     """
    
#     unified_ipos = {} # Key: (normalized_name, open_date_iso), Value: combined_data_dict

#     # 1. Process Chittorgarh All IPOs (as the base)
#     if isinstance(chittorgarh_all_ipos, list):
#         for ipo in chittorgarh_all_ipos:
#             if not isinstance(ipo, dict):
#                 print(f"Skipping malformed Chittorgarh all IPO entry: {ipo}")
#                 continue
            
#             company_name_raw = ipo.get("Company", "")
#             normalized_name = normalize_company_name(company_name_raw)
            
#             open_date_str = ipo.get("~Issue_Open_Date", "").split('T')[0] if "~Issue_Open_Date" in ipo else ""
#             open_date_dt = parse_flexible_date(open_date_str)
#             open_date_iso = open_date_dt.strftime("%Y-%m-%d") if open_date_dt else None

#             if normalized_name and open_date_iso:
#                 unique_key = (normalized_name, open_date_iso)
                
#                 unified_ipos[unique_key] = {
#                     "company_name": normalized_name.title(),
#                     "type": "Mainboard" if "mainboard" in ipo.get("Listing at", "").lower() else "SME",
#                     "opening_date": ipo.get("Opening Date", ""),
#                     "closing_date": ipo.get("Closing Date", ""),
#                     "listing_date": ipo.get("Listing Date", ""),
#                     "issue_price_rs": ipo.get("Issue Price (Rs.)", ""),
#                     "issue_amount_crcr": ipo.get("Issue Amount (Rs.cr.)", ""),
#                     "listing_at": ipo.get("Listing at", ""),
#                     "lead_manager": normalize_company_name(ipo.get("Lead Manager", "")).title(),
#                     "source_chittorgarh_basic": True,
#                     "qib_x": "", "snii_x": "", "bnii_x": "", "nii_x": "", 
#                     "retail_x": "", "employee_x": "", "others_x": "", "total_x": "", 
#                     "applications": "", "gmp_rs": "", "fire_rating": "", "est_listing_price_rs": "",
#                     "gmp_updated": "", "allotment_date": "", "refund_date": "", 
#                     "credit_to_demat_date": ""
#                 }
#     else:
#         print(f"Chittorgarh all IPOs data is not a list: {type(chittorgarh_all_ipos)}")


#     # Helper to update unified_ipos with subscription data
#     def update_subscription(subscription_list, is_sme=False, source_key="source_chittorgarh_subscription"):
#         if not isinstance(subscription_list, list):
#             print(f"Subscription data is not a list for {'SME' if is_sme else 'Mainboard'}: {type(subscription_list)}")
#             return

#         for sub in subscription_list:
#             if not isinstance(sub, dict):
#                 print(f"Skipping malformed subscription entry: {sub}")
#                 continue

#             company_name_raw = sub.get("Company Name", "")
#             normalized_name = normalize_company_name(company_name_raw)
#             close_date_str = sub.get("Close Date", "")
#             close_date_dt = parse_flexible_date(close_date_str)
            
#             open_date_str_sub = sub.get("~Issue_Open_Date", "").split('T')[0] if "~Issue_Open_Date" in sub else None
#             open_date_dt_sub = parse_flexible_date(open_date_str_sub) if open_date_str_sub else None
            
#             best_match_key = None
#             if normalized_name and close_date_dt:
#                 for key, unified_ipo in unified_ipos.items():
#                     if key[0] == normalized_name:
#                         unified_open_date_dt = parse_flexible_date(unified_ipo.get("opening_date"))

#                         if unified_open_date_dt and open_date_dt_sub and \
#                            unified_open_date_dt.date() == open_date_dt_sub.date():
#                            best_match_key = key
#                            break
#                         elif unified_open_date_dt and close_date_dt and \
#                              abs((unified_open_date_dt - close_date_dt).days) <= 7:
#                             best_match_key = key
#                             break
                        
#             if best_match_key:
#                 unified_ipos[best_match_key].update({
#                     "qib_x": sub.get("QIB (x)", ""),
#                     "nii_x": sub.get("NII (x)", ""),
#                     "retail_x": sub.get("Retail (x)", ""),
#                     "total_x": sub.get("Total (x)", ""),
#                     "applications": sub.get("Applications", ""),
#                     source_key: True
#                 })
#                 if not is_sme:
#                     unified_ipos[best_match_key].update({
#                         "snii_x": sub.get("sNII (x)", ""),
#                         "bnii_x": sub.get("bNII (x)", ""),
#                         "employee_x": sub.get("Employee (x)", ""),
#                         "others_x": sub.get("Others (x)", "")
#                     })

#     # 2. Process Chittorgarh Subscription data
#     print("  Adding Chittorgarh subscription data...")
#     update_subscription(chittorgarh_mainboard_subscription, is_sme=False, source_key="source_chittorgarh_mainboard_subscription")
#     update_subscription(chittorgarh_sme_subscription, is_sme=True, source_key="source_chittorgarh_sme_subscription")

#     # 3. Process Investorgain GMP data
#     print("  Adding Investorgain GMP data...")
#     if isinstance(investorgain_all_gmp, list):
#         for gmp_ipo in investorgain_all_gmp:
#             if not isinstance(gmp_ipo, dict):
#                 print(f"Skipping malformed Investorgain GMP entry: {gmp_ipo}")
#                 continue

#             company_name_raw = gmp_ipo.get("Name", "")
#             normalized_name = normalize_company_name(company_name_raw)
            
#             open_date_gmp_str = gmp_ipo.get("Open", "")
#             open_date_gmp_dt = parse_flexible_date(gmp_ipo.get("~Srt_Open")) if gmp_ipo.get("~Srt_Open") else \
#                                parse_flexible_date(f"{open_date_gmp_str} {datetime.now().year}")

#             open_date_gmp_iso = open_date_gmp_dt.strftime("%Y-%m-%d") if open_date_gmp_dt else None

#             best_match_key = None
#             if normalized_name and open_date_gmp_iso:
#                 for key, unified_ipo in unified_ipos.items():
#                     if key[0] == normalized_name:
#                         unified_open_date_dt = parse_flexible_date(unified_ipo.get("opening_date"))
#                         if unified_open_date_dt and open_date_gmp_dt and \
#                            unified_open_date_dt.date() == open_date_gmp_dt.date():
#                             best_match_key = key
#                             break
            
#             if not best_match_key and normalized_name:
#                  for key, unified_ipo in unified_ipos.items():
#                      if key[0] == normalized_name:
#                          best_match_key = key
#                          break

#             if best_match_key:
#                 unified_ipos[best_match_key].update({
#                     "gmp_rs": gmp_ipo.get("GMP", "").replace("&#8377;", "Rs").replace("<b>", "").replace("</b>", ""),
#                     "fire_rating": gmp_ipo.get("Fire Rating", "").replace("<span style='font-size: 12px;'>", "").replace("</span>", ""),
#                     "est_listing_price_rs": gmp_ipo.get("Est Listing", "").replace("<b>", "").replace("</b>", ""),
#                     "gmp_updated": gmp_ipo.get("GMP Updated", ""),
#                     "source_investorgain_gmp": True
#                 })
#             else:
#                 unified_ipos[(normalized_name, open_date_gmp_iso)] = {
#                     "company_name": normalized_name.title(),
#                     "opening_date": gmp_ipo.get("Open", ""),
#                     "closing_date": gmp_ipo.get("Close", ""),
#                     "listing_date": gmp_ipo.get("Listing", ""),
#                     "issue_price_rs": gmp_ipo.get("Price", ""),
#                     "issue_amount_crcr": gmp_ipo.get("IPO Size", ""),
#                     "listing_at": "",
#                     "lead_manager": "",
#                     "gmp_rs": gmp_ipo.get("GMP", "").replace("&#8377;", "Rs").replace("<b>", "").replace("</b>", ""),
#                     "fire_rating": gmp_ipo.get("Fire Rating", "").replace("<span style='font-size: 12px;'>", "").replace("</span>", ""),
#                     "est_listing_price_rs": gmp_ipo.get("Est Listing", "").replace("<b>", "").replace("</b>", ""),
#                     "gmp_updated": gmp_ipo.get("GMP Updated", ""),
#                     "source_investorgain_gmp": True,
#                     "qib_x": "", "snii_x": "", "bnii_x": "", "nii_x": "", 
#                     "retail_x": "", "employee_x": "", "others_x": "", "total_x": "", 
#                     "applications": "", "allotment_date": "", "refund_date": "", 
#                     "credit_to_demat_date": ""
#                 }
#     else:
#         print(f"Investorgain all GMP data is not a list: {type(investorgain_all_gmp)}")


#     # 4. Process Investorgain Live Subscription data
#     print("  Adding Investorgain live subscription data...")
#     if isinstance(investorgain_live_subscription, list):
#         for ig_sub in investorgain_live_subscription:
#             if not isinstance(ig_sub, dict):
#                 print(f"Skipping malformed Investorgain live subscription entry: {ig_sub}")
#                 continue

#             company_name_raw = ig_sub.get("Name", "")
#             normalized_name = normalize_company_name(company_name_raw)
            
#             open_date_ig_sub_str = ig_sub.get("Open", "")
#             close_date_ig_sub_str = ig_sub.get("Close Date", "")
#             close_date_ig_sub_dt = parse_flexible_date(close_date_ig_sub_str)
#             close_date_ig_sub_iso = close_date_ig_sub_dt.strftime("%Y-%m-%d") if close_date_ig_sub_dt else None

#             best_match_key = None
#             if normalized_name and close_date_ig_sub_iso:
#                 for key, unified_ipo in unified_ipos.items():
#                     if key[0] == normalized_name:
#                         unified_close_date_dt = parse_flexible_date(unified_ipo.get("closing_date"))
#                         if unified_close_date_dt and close_date_ig_sub_dt and \
#                            unified_close_date_dt.date() == close_date_ig_sub_dt.date():
#                             best_match_key = key
#                             break
            
#             if not best_match_key and normalized_name:
#                  for key, unified_ipo in unified_ipos.items():
#                      if key[0] == normalized_name:
#                          best_match_key = key
#                          break

#             if best_match_key:
#                 unified_ipos[best_match_key].update({
#                     "qib_x": ig_sub.get("QIB", ""),
#                     "nii_x": ig_sub.get("NII", ""),
#                     "retail_x": ig_sub.get("RII", ""),
#                     "snii_x": ig_sub.get("SHNI", ""),
#                     "bnii_x": ig_sub.get("BHNI", ""),
#                     "total_x": ig_sub.get("Total", ""),
#                     "applications": "",
#                     "source_investorgain_subscription": True
#                 })
#     else:
#         print(f"Investorgain live subscription data is not a list: {type(investorgain_live_subscription)}")


#     # 5. Process Moneycontrol IPO Calendar data
#     print("  Adding Moneycontrol calendar data...")
#     if isinstance(moneycontrol_calendar, list): # Ensure it's a list
#         for mc_ipo in moneycontrol_calendar:
#             if not isinstance(mc_ipo, dict): # Check if item is a dict
#                 print(f"Skipping malformed Moneycontrol IPO entry (not a dictionary): {mc_ipo}")
#                 continue

#             company_name_raw = mc_ipo.get("company_name", "")
#             normalized_name = normalize_company_name(company_name_raw)
            
#             open_date_mc_str = mc_ipo.get("open_date", "")
#             open_date_mc_dt = parse_flexible_date(open_date_mc_str)
#             open_date_mc_iso = open_date_mc_dt.strftime("%Y-%m-%d") if open_date_mc_dt else None

#             best_match_key = None
#             if normalized_name and open_date_mc_iso:
#                 for key, unified_ipo in unified_ipos.items():
#                     if key[0] == normalized_name and key[1] == open_date_mc_iso:
#                         best_match_key = key
#                         break
            
#             if not best_match_key and normalized_name:
#                  for key, unified_ipo in unified_ipos.items():
#                      if key[0] == normalized_name:
#                          best_match_key = key
#                          break

#             if best_match_key:
#                 unified_ipos[best_match_key].update({
#                     "allotment_date": mc_ipo.get("allotment_date", ""),
#                     "refund_date": mc_ipo.get("refund_date", ""),
#                     "credit_to_demat_date": mc_ipo.get("credit_to_demat_date", ""),
#                     "listing_date": mc_ipo.get("listing_date", ""),
#                     "source_moneycontrol_calendar": True
#                 })
#             else:
#                 unified_ipos[(normalized_name, open_date_mc_iso)] = {
#                     "company_name": normalized_name.title(),
#                     "type": "",
#                     "opening_date": mc_ipo.get("open_date", ""),
#                     "closing_date": mc_ipo.get("close_date", ""),
#                     "listing_date": mc_ipo.get("listing_date", ""),
#                     "issue_price_rs": "", "issue_amount_crcr": "",
#                     "listing_at": "", "lead_manager": "",
#                     "qib_x": "", "snii_x": "", "bnii_x": "", "nii_x": "", 
#                     "retail_x": "", "employee_x": "", "others_x": "", "total_x": "", 
#                     "applications": "", "gmp_rs": "", "fire_rating": "", "est_listing_price_rs": "",
#                     "gmp_updated": "",
#                     "allotment_date": mc_ipo.get("allotment_date", ""),
#                     "refund_date": mc_ipo.get("refund_date", ""),
#                     "credit_to_demat_date": mc_ipo.get("credit_to_demat_date", ""),
#                     "source_moneycontrol_calendar": True
#                 }
#     else:
#         print(f"Moneycontrol calendar data is not a list: {type(moneycontrol_calendar)}")

#     print("Data unification complete.")
#     return unified_ipos



# data_processors.py - UPDATED for Fire Rating Conversion
# Functions for cleaning, normalizing, and unifying IPO data.

from collections import defaultdict
import datetime
from utils import normalize_company_name, parse_flexible_date

def convert_fire_rating_to_number(rating_str):
    """
    Converts a fire rating string (e.g., containing emojis) to a numerical value (0-5).
    Assumes the rating is based on the count of '🔥' emojis or specific text.
    
    Args:
        rating_str (str): The raw fire rating string from Investorgain.
        
    Returns:
        int or None: Numerical fire rating (0-5) or None if not convertible.
    """
    if not isinstance(rating_str, str):
        return None
    
    # Clean up any HTML tags or entities that might be around the rating
    cleaned_rating = normalize_company_name(rating_str).lower().strip() # Re-use normalize_company_name for cleaning

    # --- Option 1: Count flame emojis ---
    flame_count = cleaned_rating.count('🔥')
    if flame_count > 0:
        return min(flame_count, 5) # Cap at 5 if more than 5 flames

    # --- Option 2: Handle specific text patterns (if emojis aren't consistent) ---
    # Example: "5 / 5", "4 stars", etc. Add more patterns as observed.
    if "5/5" in cleaned_rating or "5 star" in cleaned_rating:
        return 5
    elif "4/5" in cleaned_rating or "4 star" in cleaned_rating:
        return 4
    elif "3/5" in cleaned_rating or "3 star" in cleaned_rating:
        return 3
    elif "2/5" in cleaned_rating or "2 star" in cleaned_rating:
        return 2
    elif "1/5" in cleaned_rating or "1 star" in cleaned_rating:
        return 1
    elif "0/5" in cleaned_rating or "0 star" in cleaned_rating:
        return 0

    return None # Default if no match


def unify_ipo_data(
    chittorgarh_all_ipos, 
    chittorgarh_mainboard_subscription, 
    chittorgarh_sme_subscription, 
    investorgain_all_gmp, 
    investorgain_live_subscription, 
    moneycontrol_calendar
):
    """
    Unifies IPO data from various sources into a single structured format.
    
    Args:
        chittorgarh_all_ipos (list): Basic IPO data from Chittorgarh (all types).
        chittorgarh_mainboard_subscription (list): Mainboard subscription data from Chittorgarh.
        chittorgarh_sme_subscription (list): SME subscription data from Chittorgarh.
        investorgain_all_gmp (list): All GMP data from Investorgain.
        investorgain_live_subscription (list): Live subscription data from Investorgain.
        moneycontrol_calendar (list): IPO calendar data from Moneycontrol.
        
    Returns:
        dict: A dictionary where keys are unique IPO identifiers (normalized name + open date)
              and values are dictionaries of unified IPO data.
    """
    
    unified_ipos = {} # Key: (normalized_name, open_date_iso), Value: combined_data_dict

    # 1. Process Chittorgarh All IPOs (as the base)
    if isinstance(chittorgarh_all_ipos, list):
        for ipo in chittorgarh_all_ipos:
            if not isinstance(ipo, dict):
                print(f"Skipping malformed Chittorgarh all IPO entry: {ipo}")
                continue
            
            company_name_raw = ipo.get("Company", "")
            normalized_name = normalize_company_name(company_name_raw) # Use normalize_company_name from utils
            
            open_date_str = ipo.get("~Issue_Open_Date", "").split('T')[0] if "~Issue_Open_Date" in ipo else ""
            open_date_dt = parse_flexible_date(open_date_str)
            open_date_iso = open_date_dt.strftime("%Y-%m-%d") if open_date_dt else None

            if normalized_name and open_date_iso:
                unique_key = (normalized_name, open_date_iso)
                
                unified_ipos[unique_key] = {
                    "company_name": normalized_name.title(), # Title case for display
                    "type": "Mainboard" if "mainboard" in ipo.get("Listing at", "").lower() else "SME",
                    "opening_date": ipo.get("Opening Date", ""), # Original formatted date
                    "closing_date": ipo.get("Closing Date", ""),
                    "listing_date": ipo.get("Listing Date", ""),
                    "issue_price_rs": ipo.get("Issue Price (Rs.)", ""),
                    "issue_amount_crcr": ipo.get("Issue Amount (Rs.cr.)", ""),
                    "listing_at": ipo.get("Listing at", ""),
                    "lead_manager": normalize_company_name(ipo.get("Lead Manager", "")).title(),
                    "source_chittorgarh_basic": True,
                    # Initialize subscription and GMP fields
                    "qib_x": "", "snii_x": "", "bnii_x": "", "nii_x": "", 
                    "retail_x": "", "employee_x": "", "others_x": "", "total_x": "", 
                    "applications": "", "gmp_rs": "", "fire_rating": None, # Changed to None, will be numerical
                    "est_listing_price_rs": "",
                    "gmp_updated": "", "allotment_date": "", "refund_date": "", 
                    "credit_to_demat_date": ""
                }
    else:
        print(f"Chittorgarh all IPOs data is not a list: {type(chittorgarh_all_ipos)}")


    # Helper to update unified_ipos with subscription data
    def update_subscription(subscription_list, is_sme=False, source_key="source_chittorgarh_subscription"):
        if not isinstance(subscription_list, list):
            print(f"Subscription data is not a list for {'SME' if is_sme else 'Mainboard'}: {type(subscription_list)}")
            return

        for sub in subscription_list:
            if not isinstance(sub, dict):
                print(f"Skipping malformed subscription entry: {sub}")
                continue

            company_name_raw = sub.get("Company Name", "")
            normalized_name = normalize_company_name(company_name_raw)
            close_date_str = sub.get("Close Date", "")
            close_date_dt = parse_flexible_date(close_date_str)
            
            open_date_str_sub = sub.get("~Issue_Open_Date", "").split('T')[0] if "~Issue_Open_Date" in sub else None
            open_date_dt_sub = parse_flexible_date(open_date_str_sub) if open_date_str_sub else None
            
            best_match_key = None
            if normalized_name and close_date_dt:
                for key, unified_ipo in unified_ipos.items():
                    # Match by normalized name
                    if key[0] == normalized_name:
                        # Also check if dates are close (e.g., within a few days)
                        # More precisely, use the exact opening date if available from subscription API
                        unified_open_date_dt = parse_flexible_date(unified_ipo.get("opening_date"))

                        if unified_open_date_dt and open_date_dt_sub and \
                           unified_open_date_dt.date() == open_date_dt_sub.date():
                           best_match_key = key
                           break
                        elif unified_open_date_dt and close_date_dt and \
                             abs((unified_open_date_dt - close_date_dt).days) <= 7: # Allow a few days diff
                            best_match_key = key
                            break
                        
            if best_match_key:
                unified_ipos[best_match_key].update({
                    "qib_x": sub.get("QIB (x)", ""),
                    "nii_x": sub.get("NII (x)", ""),
                    "retail_x": sub.get("Retail (x)", ""),
                    "total_x": sub.get("Total (x)", ""),
                    "applications": sub.get("Applications", ""),
                    source_key: True
                })
                if not is_sme: # Mainboard has sNII and bNII
                    unified_ipos[best_match_key].update({
                        "snii_x": sub.get("sNII (x)", ""),
                        "bnii_x": sub.get("bNII (x)", ""),
                        "employee_x": sub.get("Employee (x)", ""),
                        "others_x": sub.get("Others (x)", "")
                    })

    # 2. Process Chittorgarh Subscription data
    print("  Adding Chittorgarh subscription data...")
    update_subscription(chittorgarh_mainboard_subscription, is_sme=False, source_key="source_chittorgarh_mainboard_subscription")
    update_subscription(chittorgarh_sme_subscription, is_sme=True, source_key="source_chittorgarh_sme_subscription")

    # 3. Process Investorgain GMP data
    print("  Adding Investorgain GMP data...")
    if isinstance(investorgain_all_gmp, list):
        for gmp_ipo in investorgain_all_gmp:
            if not isinstance(gmp_ipo, dict):
                print(f"Skipping malformed Investorgain GMP entry: {gmp_ipo}")
                continue

            company_name_raw = gmp_ipo.get("Name", "")
            normalized_name = normalize_company_name(company_name_raw) # Use normalize_company_name from utils
            
            open_date_gmp_str = gmp_ipo.get("Open", "")
            open_date_gmp_dt = parse_flexible_date(gmp_ipo.get("~Srt_Open")) if gmp_ipo.get("~Srt_Open") else \
                               parse_flexible_date(f"{open_date_gmp_str} {datetime.now().year}")

            open_date_gmp_iso = open_date_gmp_dt.strftime("%Y-%m-%d") if open_date_gmp_dt else None

            best_match_key = None
            if normalized_name and open_date_gmp_iso:
                for key, unified_ipo in unified_ipos.items():
                    if key[0] == normalized_name:
                        unified_open_date_dt = parse_flexible_date(unified_ipo.get("opening_date"))
                        if unified_open_date_dt and open_date_gmp_dt and \
                           unified_open_date_dt.date() == open_date_gmp_dt.date():
                            best_match_key = key
                            break
            
            if not best_match_key and normalized_name:
                 for key, unified_ipo in unified_ipos.items():
                     if key[0] == normalized_name:
                         best_match_key = key
                         break

            if best_match_key:
                unified_ipos[best_match_key].update({
                    "gmp_rs": gmp_ipo.get("GMP", "").replace("&#8377;", "Rs").replace("<b>", "").replace("</b>", ""), # Clean up HTML in GMP
                    "fire_rating": convert_fire_rating_to_number(gmp_ipo.get("Fire Rating", "")), # Convert to number here
                    "est_listing_price_rs": gmp_ipo.get("Est Listing", "").replace("<b>", "").replace("</b>", ""),
                    "gmp_updated": gmp_ipo.get("GMP Updated", ""),
                    "source_investorgain_gmp": True
                })
            else:
                unified_ipos[(normalized_name, open_date_gmp_iso)] = {
                    "company_name": normalized_name.title(),
                    "opening_date": gmp_ipo.get("Open", ""), # Use Investorgain's raw date
                    "closing_date": gmp_ipo.get("Close", ""),
                    "listing_date": gmp_ipo.get("Listing", ""),
                    "issue_price_rs": gmp_ipo.get("Price", ""),
                    "issue_amount_crcr": gmp_ipo.get("IPO Size", ""),
                    "listing_at": "", # Investorgain GMP doesn't provide this directly
                    "lead_manager": "",
                    "gmp_rs": gmp_ipo.get("GMP", "").replace("&#8377;", "Rs").replace("<b>", "").replace("</b>", ""),
                    "fire_rating": convert_fire_rating_to_number(gmp_ipo.get("Fire Rating", "")), # Convert to number here
                    "est_listing_price_rs": gmp_ipo.get("Est Listing", "").replace("<b>", "").replace("</b>", ""),
                    "gmp_updated": gmp_ipo.get("GMP Updated", ""),
                    "source_investorgain_gmp": True,
                    # Initialize other fields
                    "qib_x": "", "snii_x": "", "bnii_x": "", "nii_x": "", 
                    "retail_x": "", "employee_x": "", "others_x": "", "total_x": "", 
                    "applications": "", "allotment_date": "", "refund_date": "", 
                    "credit_to_demat_date": ""
                }
    else:
        print(f"Investorgain all GMP data is not a list: {type(investorgain_all_gmp)}")


    # 4. Process Investorgain Live Subscription data
    print("  Adding Investorgain live subscription data...")
    if isinstance(investorgain_live_subscription, list):
        for ig_sub in investorgain_live_subscription:
            if not isinstance(ig_sub, dict):
                print(f"Skipping malformed Investorgain live subscription entry: {ig_sub}")
                continue

            company_name_raw = ig_sub.get("Name", "")
            normalized_name = normalize_company_name(company_name_raw)
            
            open_date_ig_sub_str = ig_sub.get("Open", "") # Note: this field is not in provided sample schema
                                                       # If it exists, parse. Else use close date for mapping.
            # Use close date for mapping if Open is missing or less reliable
            close_date_ig_sub_str = ig_sub.get("Close Date", "")
            close_date_ig_sub_dt = parse_flexible_date(close_date_ig_sub_str)
            close_date_ig_sub_iso = close_date_ig_sub_dt.strftime("%Y-%m-%d") if close_date_ig_sub_dt else None

            best_match_key = None
            if normalized_name and close_date_ig_sub_iso:
                for key, unified_ipo in unified_ipos.items():
                    if key[0] == normalized_name:
                        unified_close_date_dt = parse_flexible_date(unified_ipo.get("closing_date"))
                        if unified_close_date_dt and close_date_ig_sub_dt and \
                           unified_close_date_dt.date() == close_date_ig_sub_dt.date():
                            best_match_key = key
                            break
            
            if not best_match_key and normalized_name:
                 for key, unified_ipo in unified_ipos.items():
                     if key[0] == normalized_name:
                         best_match_key = key
                         break

            if best_match_key:
                unified_ipos[best_match_key].update({
                    "qib_x": ig_sub.get("QIB", ""),
                    "nii_x": ig_sub.get("NII", ""),
                    "retail_x": ig_sub.get("RII", ""),
                    "snii_x": ig_sub.get("SHNI", ""), # Small HNI
                    "bnii_x": ig_sub.get("BHNI", ""), # Big HNI
                    "total_x": ig_sub.get("Total", ""),
                    "applications": "", # Investorgain Live Sub doesn't have explicit applications count in provided schema
                    "source_investorgain_subscription": True
                })
    else:
        print(f"Investorgain live subscription data is not a list: {type(investorgain_live_subscription)}")


    # 5. Process Moneycontrol IPO Calendar data
    print("  Adding Moneycontrol calendar data...")
    if isinstance(moneycontrol_calendar, list): # Ensure it's a list
        for mc_ipo in moneycontrol_calendar:
            if not isinstance(mc_ipo, dict): # Check if item is a dict
                print(f"Skipping malformed Moneycontrol IPO entry (not a dictionary): {mc_ipo}")
                continue

            company_name_raw = mc_ipo.get("company_name", "")
            normalized_name = normalize_company_name(company_name_raw)
            
            open_date_mc_str = mc_ipo.get("open_date", "")
            open_date_mc_dt = parse_flexible_date(open_date_mc_str)
            open_date_mc_iso = open_date_mc_dt.strftime("%Y-%m-%d") if open_date_mc_dt else None

            best_match_key = None
            if normalized_name and open_date_mc_iso:
                for key, unified_ipo in unified_ipos.items():
                    if key[0] == normalized_name and key[1] == open_date_mc_iso:
                        best_match_key = key
                        break
            
            if not best_match_key and normalized_name:
                 for key, unified_ipo in unified_ipos.items():
                     if key[0] == normalized_name:
                         best_match_key = key
                         break

            if best_match_key:
                unified_ipos[best_match_key].update({
                    "allotment_date": mc_ipo.get("allotment_date", ""),
                    "refund_date": mc_ipo.get("refund_date", ""),
                    "credit_to_demat_date": mc_ipo.get("credit_to_demat_date", ""),
                    "listing_date": mc_ipo.get("listing_date", ""),
                    "source_moneycontrol_calendar": True
                })
            else:
                unified_ipos[(normalized_name, open_date_mc_iso)] = {
                    "company_name": normalized_name.title(),
                    "type": "",
                    "opening_date": mc_ipo.get("open_date", ""),
                    "closing_date": mc_ipo.get("close_date", ""),
                    "listing_date": mc_ipo.get("listing_date", ""),
                    "issue_price_rs": "", "issue_amount_crcr": "",
                    "listing_at": "", "lead_manager": "",
                    "qib_x": "", "snii_x": "", "bnii_x": "", "nii_x": "", 
                    "retail_x": "", "employee_x": "", "others_x": "", "total_x": "", 
                    "applications": "", "gmp_rs": "", "fire_rating": None, # Initialize as None
                    "est_listing_price_rs": "",
                    "gmp_updated": "",
                    "allotment_date": mc_ipo.get("allotment_date", ""),
                    "refund_date": mc_ipo.get("refund_date", ""),
                    "credit_to_demat_date": mc_ipo.get("credit_to_demat_date", ""),
                    "source_moneycontrol_calendar": True
                }
    else:
        print(f"Moneycontrol calendar data is not a list: {type(moneycontrol_calendar)}")

    print("Data unification complete.")
    return unified_ipos
