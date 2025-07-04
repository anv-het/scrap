import requests
import pyodbc
import re
from datetime import datetime
import json

# --- Configuration ---
API_URL = "https://webnodejs.investorgain.com/cloud/report/data-read/331/1/7/2025/2025-26/0/all?search=&v=10-12"

# MSSQL Connection details
DB_CONFIG = {
    'driver': '{ODBC Driver 17 for SQL Server}',
    'server': '192.168.102.120',
    'database': 'E-IPO',
    'uid': 'sa',
    'pwd': '963852'
}

TABLE_NAME = "current_ipo_data"

# --- Data Cleaning and Transformation Functions ---

def to_snake_case(name):
    """Converts a string to snake_case."""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower().replace('~', '')

def clean_data(data):
    """Cleans and transforms a single raw IPO item dictionary."""
    cleaned_item = {}
    # Use the current year for dates that only provide day and month
    current_year = datetime.now().year 

    for key, value in data.items():
        snake_case_key = to_snake_case(key)
        
        # 1. Name: Extract text from title attribute or clean HTML
        if key == "Name":
            match = re.search(r'title="(.*?)"', value)
            if match:
                cleaned_item[snake_case_key] = match.group(1)
            else:
                # Fallback if title attribute not found, clean other HTML/text
                clean_name = re.sub(r'<[^>]+>|\s(IPO|NSE|BSE)\s(SME)?\s?[UOCLT@].*', '', value).strip()
                clean_name = re.sub(r'L@\d+\.?\d*\s*\(.*\)', '', clean_name).strip() # Further cleanup
                cleaned_item[snake_case_key] = clean_name
        
        # 2. GMP: Extract premium (bold) and percentage (in parentheses)
        elif key == "GMP":
            gmp_match = re.search(r'&#8377;<b>([\d\.]+)</b>\s?\((\d+\.?\d*)%\)', value)
            if gmp_match:
                cleaned_item['gmp_premium'] = gmp_match.group(1)
                cleaned_item['gmp_percent'] = gmp_match.group(2)
            else:
                # Fallback if the pattern doesn't match perfectly, try to get anything
                gmp_match_fallback = re.search(r'([\d\.]+)\s?\((\d+\.?\d*)%\)', value)
                if gmp_match_fallback:
                    cleaned_item['gmp_premium'] = gmp_match_fallback.group(1)
                    cleaned_item['gmp_percent'] = gmp_match_fallback.group(2)
                else:
                    cleaned_item['gmp_premium'] = None
                    cleaned_item['gmp_percent'] = None
        
        # 3. Fire Rating: Count flame emojis
        elif key == "Fire Rating":
            cleaned_item['fire_rating'] = value.count('&#128293;')
        
        # 4. Est Listing: Extract bold estimated price
        elif key == "IPO Size":
            print(f"DEBUG: Processing 'IPO Size'. Raw value: '{value}'")
            ipo_size_match = re.search(r'&#8377;([\d\.]+\s?Cr)', value) # Capture "Number Cr"
            if ipo_size_match:
                extracted_value = ipo_size_match.group(1)
                cleaned_item[snake_case_key] = extracted_value
                print(f"DEBUG: 'IPO Size' matched pattern. Extracted: '{extracted_value}'")
            else:
                ipo_size_fallback = re.search(r'([\d\.]+)', value) # Fallback for just a number
                if ipo_size_fallback:
                    extracted_value = ipo_size_fallback.group(1)
                    cleaned_item[snake_case_key] = extracted_value
                    print(f"DEBUG: 'IPO Size' fallback matched. Extracted: '{extracted_value}'")
                else:
                    cleaned_item[snake_case_key] = None
                    print(f"DEBUG: 'IPO Size' no match found, set to None.")

        # 5. IPO Size: Extract numeric value before 'Cr'
        # DEBUGGING: Est Listing
        if key == "Est Listing":
            print(f"DEBUG: Processing 'Est Listing'. Raw value: '{value}'")
            est_listing_match = re.search(r'<b>([\d\.]+)</b>\s?\((\d+\.?\d*)%\)', value)
            if est_listing_match:
                extracted_value = est_listing_match.group(1)
                cleaned_item[snake_case_key] = extracted_value
                print(f"DEBUG: 'Est Listing' matched pattern. Extracted: '{extracted_value}'")
            elif value.strip() == '--':
                cleaned_item[snake_case_key] = None
                print(f"DEBUG: 'Est Listing' is '--', set to None.")
            else:
                match_fallback = re.search(r'(\d+\.?\d*)', value)
                if match_fallback:
                    extracted_value = match_fallback.group(1)
                    cleaned_item[snake_case_key] = extracted_value
                    print(f"DEBUG: 'Est Listing' fallback matched. Extracted: '{extracted_value}'")
                else:
                    cleaned_item[snake_case_key] = None
                    print(f"DEBUG: 'Est Listing' no match found, set to None.")
        
        # 6. GMP Updated: Parse date/time with current year
        elif key == "GMP Updated":
            try:
                gmp_updated_str = f"{value} {current_year}"
                # Handle potential issue if time is not always present (e.g., '1-Jul')
                if re.search(r'\d+-\w+\s\d+:\d+', value): # Has time
                    cleaned_item['gmp_updated_at'] = datetime.strptime(gmp_updated_str, "%d-%b %H:%M %Y").strftime("%Y-%m-%d %H:%M:%S")
                else: # No time, just date
                    cleaned_item['gmp_updated_at'] = datetime.strptime(gmp_updated_str, "%d-%b %Y").strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                cleaned_item['gmp_updated_at'] = None
        
        # 7. ID: Directly assign ~id
        elif key == "~id":
            cleaned_item['id'] = value
        
        # 8. Date Fields: Map ~Srt_ and ~Str_ to both _date and srt_*/str_* columns
        elif key == "~Srt_Open":
            cleaned_item['open_date'] = value # For open_date column
            cleaned_item[snake_case_key] = value # For srt_open column
        elif key == "~Srt_Close":
            cleaned_item['close_date'] = value # For close_date column
            cleaned_item[snake_case_key] = value # For srt_close column
        elif key == "~Srt_BoA_Dt":
            cleaned_item['boa_date'] = value # For boa_date column
            cleaned_item[snake_case_key] = value # For srt_boa_dt column
        elif key == "~Str_Listing":
            cleaned_item['listing_date'] = value # For listing_date column
            cleaned_item[snake_case_key] = value # For str_listing column
        
        # Skip the redundant "Open", "Close", "BoA Dt", "Listing" fields
        elif key in ["Open", "Close", "BoA Dt", "Listing"]:
            continue
        
        # Ensure other tilde-prefixed sort fields are also snake_cased and stored
        elif key.startswith("~Srt_") or key.startswith("~Str_"):
             cleaned_item[snake_case_key] = value

        # 9. P/E: Handle '~P/E' explicitly for 'p_e'
        elif key == "~P/E":
            cleaned_item['p_e'] = value
        
        # 10. Display Order: Handle '~Display_Order'
        elif key == "~Display_Order":
            cleaned_item['display_order'] = value
            
        # 11. Highlight Row: Handle '~Highlight_Row'
        elif key == "~Highlight_Row":
            cleaned_item['highlight_row'] = value
            
        # 12. IPO Category: Handle '~IPO_Category'
        elif key == "~IPO_Category":
            cleaned_item['ipo_category'] = value

        # General handling for other fields: remove HTML and normalize empty/placeholder values
        else:
            clean_value = re.sub(r'<[^>]+>', '', str(value)).strip()
            if clean_value == '' or clean_value == '--' or clean_value == 'TBD':
                cleaned_item[snake_case_key] = None
            else:
                cleaned_item[snake_case_key] = clean_value

    # No need to remove 'orderby' keys here explicitly if to_snake_case handles '~orderby' implicitly,
    # and other '~' prefixed keys are handled directly in the if/elif chain.
    # This loop was meant for generic tilde keys that we don't want in final output, but are already mapped.
    # Let's remove the catch-all for '~' prefixed keys if they are not explicitly mapped above
    # and ensure only the desired snake_case keys remain.
    final_keys_to_keep = [
        'id', 'name', 'gmp_premium', 'gmp_percent', 'fire_rating', 'sub', 'price',
        'est_listing', 'ipo_size', 'lot', 'p_e', 'open_date', 'close_date',
        'boa_date', 'listing_date', 'srt_open', 'srt_close', 'srt_boa_dt',
        'str_listing', 'urlrewrite_folder_name', 'gmp_updated_at',
        'display_order', 'highlight_row', 'ipo_category'
    ]
    
    # Create a new dictionary with only the desired keys
    final_cleaned_item = {k: cleaned_item.get(k) for k in final_keys_to_keep}

    return final_cleaned_item


# --- Main Script (remains largely the same, just copied for completeness) ---
def fetch_and_save_ipo_data():
    """Fetches IPO data from API, cleans it, and saves it to MSSQL."""
    try:
        print("Fetching data from API...")
        response = requests.get(API_URL)
        response.raise_for_status()  # Raise an exception for HTTP errors
        raw_api_response = response.json()
        print("Data fetched successfully.")

        print(f"DEBUG: Full raw API response keys: {raw_api_response.keys()}")

        raw_ipo_items = raw_api_response.get('reportTableData')

        print(f"DEBUG: Type of raw_ipo_items: {type(raw_ipo_items)}")

        if not isinstance(raw_ipo_items, list):
            if raw_ipo_items is None:
                print("Error: 'reportTableData' key not found or its value is None.")
            else:
                print(f"Error: 'reportTableData' content is not a list. Type: {type(raw_ipo_items)}. Aborting.")
            return

        if not raw_ipo_items:
            print("No IPO items found in 'reportTableData'.")
            return

        cleaned_data_list = []
        for item in raw_ipo_items:
            # We added a check for '~id' in the `clean_data` function,
            # so this check here is somewhat redundant if `clean_data` handles it.
            # However, keeping it here for immediate skipping if a raw item truly lacks an ID.
            if '~id' not in item:
                print(f"WARNING: IPO item missing '~id' before cleaning: {item}. Skipping.")
                continue
            
            cleaned_data_list.append(clean_data(item))
            
        print("Data cleaned and transformed.")
        # Optional: Print first cleaned item for inspection
        if cleaned_data_list:
           print(f"DEBUG: First cleaned item: {cleaned_data_list[0]}")


        # --- MSSQL Insertion ---
        conn = None
        cursor = None
        try:
            conn = pyodbc.connect(
                'DRIVER={};SERVER={};DATABASE={};UID={};PWD={}'.format(
                    DB_CONFIG['driver'], DB_CONFIG['server'], DB_CONFIG['database'], DB_CONFIG['uid'], DB_CONFIG['pwd']
                )
            )
            cursor = conn.cursor()
            print("Connected to MSSQL database.")

            # Ensure columns are correctly typed for cleaned data
            create_table_query = f"""
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name='{TABLE_NAME}')
            BEGIN
                CREATE TABLE {TABLE_NAME} (
                    id INT PRIMARY KEY,
                    name NVARCHAR(255),
                    gmp_premium NVARCHAR(50),
                    gmp_percent NVARCHAR(50),
                    fire_rating INT,
                    sub NVARCHAR(50),
                    price NVARCHAR(50),
                    est_listing NVARCHAR(50),
                    ipo_size NVARCHAR(50),
                    lot NVARCHAR(50),
                    p_e NVARCHAR(50),
                    open_date DATE,           
                    close_date DATE,          
                    boa_date DATE,            
                    listing_date DATE,        
                    srt_open DATE,          
                    srt_close DATE,
                    srt_boa_dt DATE,
                    str_listing DATE,
                    urlrewrite_folder_name NVARCHAR(255),
                    gmp_updated_at DATETIME,
                    display_order INT,
                    highlight_row NVARCHAR(50),
                    ipo_category NVARCHAR(50),
                    created_at DATETIME DEFAULT GETDATE(),
                    updated_at DATETIME DEFAULT GETDATE()
                );
            END;
            """
            cursor.execute(create_table_query)
            conn.commit()
            print(f"Table '{TABLE_NAME}' ensured to exist.")

            for item in cleaned_data_list:
                item_id = item.get('id')
                if item_id is None:
                    print(f"Warning: 'id' is None after cleaning for item: {item}. Skipping insertion.")
                    continue
                
                try:
                    item_id = int(item_id)
                except (ValueError, TypeError):
                    print(f"Warning: Could not convert 'id' ({item_id}) to integer for item: {item}. Skipping insertion.")
                    continue

                db_columns_for_update_insert = [
                    'name', 'gmp_premium', 'gmp_percent', 'fire_rating', 'sub', 'price',
                    'est_listing', 'ipo_size', 'lot', 'p_e', 'open_date', 'close_date',
                    'boa_date', 'listing_date', 'srt_open', 'srt_close', 'srt_boa_dt',
                    'str_listing', 'urlrewrite_folder_name', 'gmp_updated_at',
                    'display_order', 'highlight_row', 'ipo_category'
                ]

                prepared_item_values = []
                for col in db_columns_for_update_insert:
                    val = item.get(col)
                    if isinstance(val, str) and (val.strip() == '' or val.strip() == '--' or val.strip() == 'TBD'):
                        prepared_item_values.append(None)
                    else:
                        prepared_item_values.append(val)

                check_exists_query = f"SELECT COUNT(*) FROM {TABLE_NAME} WHERE id = ?"
                cursor.execute(check_exists_query, item_id)
                exists = cursor.fetchone()[0] > 0

                if exists:
                    update_set_clauses = [f"{col} = ?" for col in db_columns_for_update_insert]
                    update_query = f"""
                        UPDATE {TABLE_NAME}
                        SET {', '.join(update_set_clauses)}, updated_at = GETDATE()
                        WHERE id = ?
                    """
                    update_params = prepared_item_values + [item_id]
                    cursor.execute(update_query, update_params)
                    print(f"Updated record with ID: {item_id}")
                else:
                    insert_columns = ', '.join(['id'] + db_columns_for_update_insert + ['created_at', 'updated_at'])
                    insert_placeholders = ', '.join(['?' for _ in (['id'] + db_columns_for_update_insert)]) + ', GETDATE(), GETDATE()'
                    insert_params = [item_id] + prepared_item_values

                    insert_query = f"""
                        INSERT INTO {TABLE_NAME} ({insert_columns})
                        VALUES ({insert_placeholders})
                    """
                    cursor.execute(insert_query, insert_params)
                    print(f"Inserted new record with ID: {item_id}")
                    
                conn.commit()

            print("Data successfully saved/updated in MSSQL.")

        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Database error: {sqlstate} - {ex}")
            if conn:
                conn.rollback()
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
            print("MSSQL connection closed.")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    fetch_and_save_ipo_data()
