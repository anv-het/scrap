import streamlit as st
import requests
import pyodbc
import pandas as pd
import re
from datetime import datetime
from bs4 import BeautifulSoup
import json
from typing import Dict, Any, List

# Database Configuration
DB_CONFIG = {
    'driver': '{ODBC Driver 17 for SQL Server}',
    'server': '192.168.102.120',
    'database': 'E-IPO',
    'username': 'sa',
    'password': '963852'
}

# API Configuration
API_URL = "https://webnodejs.investorgain.com/cloud/report/data-read/331/1/7/2025/2025-26/0/all"

class IPODataProcessor:
    def __init__(self):
        self.current_year = datetime.now().year
    
    def clean_html_content(self, html_content: str) -> str:
        """Remove HTML tags and extract clean text"""
        if not html_content or not isinstance(html_content, str):
            return ""
        
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text(strip=True)
    
    def extract_gmp_data(self, gmp_text: str) -> tuple:
        """Extract GMP premium and percentage from GMP field"""
        if not gmp_text:
            return "", ""
        
        # Remove HTML entities and tags
        clean_text = self.clean_html_content(gmp_text)
        clean_text = clean_text.replace('₹', '').replace('&#8377;', '')
        
        # Extract number and percentage using regex
        number_match = re.search(r'(\d+(?:\.\d+)?)', clean_text)
        percent_match = re.search(r'\((\d+(?:\.\d+)?)%\)', clean_text)
        
        premium = number_match.group(1) if number_match else ""
        percentage = percent_match.group(1) if percent_match else ""
        
        return premium, percentage
    
    def extract_fire_rating(self, fire_rating_text: str) -> str:
        """Count fire emojis and return count"""
        if not fire_rating_text:
            return "0"
        
        # Count fire emoji occurrences
        fire_count = fire_rating_text.count('&#128293;')
        return str(fire_count)
    
    def extract_est_listing(self, est_listing_text: str) -> str:
        """Extract estimated listing price"""
        if not est_listing_text:
            return ""
        
        clean_text = self.clean_html_content(est_listing_text)
        number_match = re.search(r'(\d+(?:\.\d+)?)', clean_text)
        return number_match.group(1) if number_match else ""
    
    def extract_ipo_size(self, ipo_size_text: str) -> str:
        """Extract IPO size removing currency symbol"""
        if not ipo_size_text:
            return ""
        
        clean_text = ipo_size_text.replace('₹', '').replace('&#8377;', '').strip()
        return clean_text
    
    def parse_date_with_year(self, date_str: str) -> str:
        """Convert date format like '30-Jun' to '2025-06-30'"""
        if not date_str:
            return ""
        
        try:
            # Parse date and add current year
            date_obj = datetime.strptime(f"{date_str} {self.current_year}", "%d-%b %Y")
            return date_obj.strftime("%Y-%m-%d")
        except:
            return ""
    
    def parse_datetime_with_year(self, datetime_str: str) -> str:
        """Convert datetime format like '1-Jul 10:02' to '2025-07-01 10:02'"""
        if not datetime_str:
            return ""
        
        try:
            # Parse datetime and add current year
            datetime_obj = datetime.strptime(f"{datetime_str} {self.current_year}", "%d-%b %H:%M %Y")
            return datetime_obj.strftime("%Y-%m-%d %H:%M")
        except:
            return ""
    
    def convert_to_snake_case(self, key: str) -> str:
        """Convert key to snake_case"""
        # Remove special characters and tildes
        key = key.replace('~', '').replace(' ', '_')
        
        # Convert to snake_case
        key = re.sub('([A-Z]+)', r'_\1', key).lower()
        key = key.strip('_')
        
        return key
    
    def clean_and_transform_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and transform the raw API data"""
        cleaned_data = {}
        
        for key, value in raw_data.items():
            snake_key = self.convert_to_snake_case(key)
            
            # Handle specific fields
            if key == "Name":
                cleaned_data['name'] = self.clean_html_content(str(value))
            elif key == "GMP":
                premium, percentage = self.extract_gmp_data(str(value))
                cleaned_data['gmp_premium'] = premium
                cleaned_data['gmp_percent'] = percentage
            elif key == "Fire Rating":
                cleaned_data['fire_rating'] = self.extract_fire_rating(str(value))
            elif key == "Est Listing":
                cleaned_data['est_listing'] = self.extract_est_listing(str(value))
            elif key == "IPO Size":
                cleaned_data['ipo_size'] = self.extract_ipo_size(str(value))
            elif key == "Open":
                cleaned_data['open_date'] = self.parse_date_with_year(str(value))
            elif key == "Close":
                cleaned_data['close_date'] = self.parse_date_with_year(str(value))
            elif key == "BoA Dt":
                cleaned_data['boa_date'] = self.parse_date_with_year(str(value))
            elif key == "Listing":
                cleaned_data['listing_date'] = self.parse_date_with_year(str(value))
            elif key == "GMP Updated":
                cleaned_data['gmp_updated_at'] = self.parse_datetime_with_year(str(value))
            elif key.startswith('~'):
                # Handle keys with tilde prefix
                if key == "~P/E":
                    cleaned_data['p_e'] = str(value) if value else ""
                elif key == "~id":
                    cleaned_data['id'] = int(value) if value else 0
                elif key == "~Srt_Open":
                    cleaned_data['srt_open'] = str(value) if value else ""
                elif key == "~Srt_Close":
                    cleaned_data['srt_close'] = str(value) if value else ""
                elif key == "~Srt_BoA_Dt":
                    cleaned_data['srt_boa_dt'] = str(value) if value else ""
                elif key == "~Str_Listing":
                    cleaned_data['str_listing'] = str(value) if value else ""
                elif key == "~urlrewrite_folder_name":
                    cleaned_data['urlrewrite_folder_name'] = str(value) if value else ""
                elif key == "~Display_Order":
                    cleaned_data['display_order'] = int(value) if value else 0
                elif key == "~Highlight_Row":
                    cleaned_data['highlight_row'] = str(value) if value else ""
                elif key == "~IPO_Category":
                    cleaned_data['ipo_category'] = str(value) if value else ""
            else:
                # Handle other fields
                if key.lower() in ['sub', 'price', 'lot']:
                    cleaned_data[snake_key] = str(value) if value else ""
                else:
                    cleaned_data[snake_key] = str(value) if value else ""
        
        return cleaned_data

class DatabaseManager:
    def __init__(self, config: Dict[str, str]):
        self.config = config
    
    def get_connection(self):
        """Create database connection"""
        conn_str = (
            f"DRIVER={self.config['driver']};"
            f"SERVER={self.config['server']};"
            f"DATABASE={self.config['database']};"
            f"UID={self.config['username']};"
            f"PWD={self.config['password']};"
            "Trusted_Connection=no;"
        )
        return pyodbc.connect(conn_str)
    
    def create_table_if_not_exists(self):
        """Create IPO data table if it doesn't exist"""
        create_table_sql = """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='current_ipo_data' AND xtype='U')
        CREATE TABLE current_ipo_data (
            id INT PRIMARY KEY,
            name NVARCHAR(255),
            gmp_premium NVARCHAR(50),
            gmp_percent NVARCHAR(50),
            fire_rating NVARCHAR(10),
            sub NVARCHAR(50),
            price NVARCHAR(50),
            est_listing NVARCHAR(50),
            ipo_size NVARCHAR(100),
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
            urlrewrite_folder_name NVARCHAR(500),
            gmp_updated_at DATETIME,
            display_order INT,
            highlight_row NVARCHAR(100),
            ipo_category NVARCHAR(50),
            created_at DATETIME DEFAULT GETDATE(),
            updated_at DATETIME DEFAULT GETDATE()
        )
        """
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(create_table_sql)
            conn.commit()
    
    def insert_or_update_data(self, data: Dict[str, Any]) -> bool:
        """Insert or update IPO data"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if record exists
                check_sql = "SELECT COUNT(*) FROM current_ipo_data WHERE id = ?"
                cursor.execute(check_sql, (data['id'],))
                exists = cursor.fetchone()[0] > 0
                
                if exists:
                    # Update existing record
                    update_sql = """
                    UPDATE ipo_data SET 
                        name = ?, gmp_premium = ?, gmp_percent = ?, fire_rating = ?,
                        sub = ?, price = ?, est_listing = ?, ipo_size = ?, lot = ?,
                        p_e = ?, open_date = ?, close_date = ?, boa_date = ?,
                        listing_date = ?, srt_open = ?, srt_close = ?, srt_boa_dt = ?,
                        str_listing = ?, urlrewrite_folder_name = ?, gmp_updated_at = ?,
                        display_order = ?, highlight_row = ?, ipo_category = ?,
                        updated_at = GETDATE()
                    WHERE id = ?
                    """
                    
                    cursor.execute(update_sql, (
                        data.get('name', ''), data.get('gmp_premium', ''), 
                        data.get('gmp_percent', ''), data.get('fire_rating', ''),
                        data.get('sub', ''), data.get('price', ''), 
                        data.get('est_listing', ''), data.get('ipo_size', ''),
                        data.get('lot', ''), data.get('p_e', ''),
                        data.get('open_date') or None, data.get('close_date') or None,
                        data.get('boa_date') or None, data.get('listing_date') or None,
                        data.get('srt_open') or None, data.get('srt_close') or None,
                        data.get('srt_boa_dt') or None, data.get('str_listing') or None,
                        data.get('urlrewrite_folder_name', ''), 
                        data.get('gmp_updated_at') or None,
                        data.get('display_order', 0), data.get('highlight_row', ''),
                        data.get('ipo_category', ''), data['id']
                    ))
                else:
                    # Insert new record
                    insert_sql = """
                    INSERT INTO current_ipo_data (
                        id, name, gmp_premium, gmp_percent, fire_rating, sub, price,
                        est_listing, ipo_size, lot, p_e, open_date, close_date,
                        boa_date, listing_date, srt_open, srt_close, srt_boa_dt,
                        str_listing, urlrewrite_folder_name, gmp_updated_at,
                        display_order, highlight_row, ipo_category
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    
                    cursor.execute(insert_sql, (
                        data['id'], data.get('name', ''), data.get('gmp_premium', ''),
                        data.get('gmp_percent', ''), data.get('fire_rating', ''),
                        data.get('sub', ''), data.get('price', ''), 
                        data.get('est_listing', ''), data.get('ipo_size', ''),
                        data.get('lot', ''), data.get('p_e', ''),
                        data.get('open_date') or None, data.get('close_date') or None,
                        data.get('boa_date') or None, data.get('listing_date') or None,
                        data.get('srt_open') or None, data.get('srt_close') or None,
                        data.get('srt_boa_dt') or None, data.get('str_listing') or None,
                        data.get('urlrewrite_folder_name', ''), 
                        data.get('gmp_updated_at') or None,
                        data.get('display_order', 0), data.get('highlight_row', ''),
                        data.get('ipo_category', '')
                    ))
                
                conn.commit()
                return True
                
        except Exception as e:
            st.error(f"Database error: {str(e)}")
            return False

def fetch_api_data(url: str, params: dict = None) -> List[Dict]:
    """Fetch data from API"""
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        # Try to parse as JSON
        try:
            data = response.json()
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                return [data]
            else:
                st.error("Unexpected data format from API")
                return []
        except json.JSONDecodeError:
            st.error("Failed to parse JSON response")
            return []
            
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {str(e)}")
        return []

def main():
    st.set_page_config(
        page_title="IPO Data Fetcher",
        page_icon="📈",
        layout="wide"
    )
    
    st.title("📈 IPO Data Fetcher & Database Manager")
    st.markdown("Fetch IPO data from API, clean it, and save to MSSQL database")
    
    # Sidebar for configuration
    st.sidebar.header("Configuration")
    
    # Database configuration
    st.sidebar.subheader("Database Settings")
    db_server = st.sidebar.text_input("Server", value=DB_CONFIG['server'])
    db_database = st.sidebar.text_input("Database", value=DB_CONFIG['database'])
    db_username = st.sidebar.text_input("Username", value=DB_CONFIG['username'])
    db_password = st.sidebar.text_input("Password", type="password", value=DB_CONFIG['password'])
    
    # Update DB_CONFIG
    DB_CONFIG.update({
        'server': db_server,
        'database': db_database,
        'username': db_username,
        'password': db_password
    })
    
    # API configuration
    st.sidebar.subheader("API Settings")
    api_url = st.sidebar.text_input("API URL", value=API_URL)
    
    # Initialize classes
    processor = IPODataProcessor()
    db_manager = DatabaseManager(DB_CONFIG)
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("Fetch & Process Data")
        
        if st.button("🚀 Fetch Data from API", type="primary"):
            with st.spinner("Fetching data from API..."):
                raw_data_list = fetch_api_data(api_url)
                
                if raw_data_list:
                    st.success(f"Fetched {len(raw_data_list)} records from API")
                    
                    # Create table if not exists
                    with st.spinner("Setting up database..."):
                        try:
                            db_manager.create_table_if_not_exists()
                            st.success("Database table ready")
                        except Exception as e:
                            st.error(f"Database setup failed: {str(e)}")
                            return
                    
                    # Process and save data
                    success_count = 0
                    error_count = 0
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for i, raw_data in enumerate(raw_data_list):
                        try:
                            # Clean and transform data
                            cleaned_data = processor.clean_and_transform_data(raw_data)
                            
                            # Save to database
                            if db_manager.insert_or_update_data(cleaned_data):
                                success_count += 1
                            else:
                                error_count += 1
                            
                            # Update progress
                            progress = (i + 1) / len(raw_data_list)
                            progress_bar.progress(progress)
                            status_text.text(f"Processing record {i + 1} of {len(raw_data_list)}")
                            
                        except Exception as e:
                            st.error(f"Error processing record {i + 1}: {str(e)}")
                            error_count += 1
                    
                    # Final status
                    st.success(f"✅ Successfully processed {success_count} records")
                    if error_count > 0:
                        st.warning(f"⚠️ {error_count} records had errors")
                else:
                    st.error("No data received from API")
    
    with col2:
        st.header("Data Preview")
        
        if st.button("👀 Preview Sample Data"):
            sample_data = fetch_api_data(api_url)
            if sample_data:
                st.subheader("Raw Data Sample")
                st.json(sample_data[0] if sample_data else {})
                
                st.subheader("Cleaned Data Sample")
                cleaned_sample = processor.clean_and_transform_data(sample_data[0])
                st.json(cleaned_sample)
    
    # Data viewer
    st.header("📊 Database Data Viewer")
    
    if st.button("🔍 View Saved Data"):
        try:
            with db_manager.get_connection() as conn:
                df = pd.read_sql("SELECT TOP 100 * FROM current_ipo_data ORDER BY updated_at DESC", conn)
                if not df.empty:
                    st.dataframe(df, use_container_width=True)
                    
                    # Download option
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name=f"current_ipo_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.info("No data found in database")
        except Exception as e:
            st.error(f"Error viewing data: {str(e)}")

if __name__ == "__main__":
    main()

