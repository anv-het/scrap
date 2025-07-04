# Configuration file for IPO Data Fetcher
# Copy this file and update with your actual database credentials

# Database Configuration
DB_CONFIG = {
    'driver': '{ODBC Driver 17 for SQL Server}',  # or '{SQL Server}' for older versions
    'server': '192.168.102.120',          # e.g., 'localhost' or '192.168.1.100'
    'database': 'E-IPO',            # e.g., 'IPOData'
    'username': 'sa',                 # e.g., 'sa' or your SQL Server username
    'password': '963852'                  # Your SQL Server password
}

# API Configuration
API_CONFIG = {
    'base_url': 'https://webnodejs.investorgain.com/cloud/report/data-read/331/1/7/2025/2025-26/0/all',
    'timeout': 30,
    'retry_attempts': 3
}

# Application Settings
APP_CONFIG = {
    'page_title': 'IPO Data Fetcher',
    'page_icon': '📈',
    'layout': 'wide',
    'batch_size': 100  # Number of records to process in one batch
}

# Data Processing Settings
PROCESSING_CONFIG = {
    'current_year': 2025,
    'date_format': '%Y-%m-%d',
    'datetime_format': '%Y-%m-%d %H:%M',
    'default_fire_rating': '0'
}

# Database Table Schema
TABLE_SCHEMA = {
    'table_name': 'current_ipo_data',
    'primary_key': 'id',
    'columns': {
        'id': 'INT PRIMARY KEY',
        'name': 'NVARCHAR(255)',
        'gmp_premium': 'NVARCHAR(50)',
        'gmp_percent': 'NVARCHAR(50)',
        'fire_rating': 'NVARCHAR(10)',
        'sub': 'NVARCHAR(50)',
        'price': 'NVARCHAR(50)',
        'est_listing': 'NVARCHAR(50)',
        'ipo_size': 'NVARCHAR(100)',
        'lot': 'NVARCHAR(50)',
        'p_e': 'NVARCHAR(50)',
        'open_date': 'DATE',
        'close_date': 'DATE',
        'boa_date': 'DATE',
        'listing_date': 'DATE',
        'srt_open': 'DATE',
        'srt_close': 'DATE',
        'srt_boa_dt': 'DATE',
        'str_listing': 'DATE',
        'urlrewrite_folder_name': 'NVARCHAR(500)',
        'gmp_updated_at': 'DATETIME',
        'display_order': 'INT',
        'highlight_row': 'NVARCHAR(100)',
        'ipo_category': 'NVARCHAR(50)',
        'created_at': 'DATETIME DEFAULT GETDATE()',
        'updated_at': 'DATETIME DEFAULT GETDATE()'
    }
}