
CHITTORGARH_BASE_URL = "https://webnodejs.chittorgarh.com/cloud/report/data-read"
INVESTORGAIN_BASE_URL = "https://webnodejs.investorgain.com/cloud/report/data-read"
MONEYCONTROL_CALENDAR_URL = "https://api.moneycontrol.com/mcapi/v1/ipo/calendar-data"

# Common headers to mimic a browser and ensure API access
COMMON_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd", # Added 'br' for Brotli
    "Connection": "keep-alive"
}

# Specific headers for Chittorgarh
CHITTORGARH_HEADERS = {
    **COMMON_HEADERS,
    "Origin": "https://www.chittorgarh.com",
    "Referer": "https://www.chittorgarh.com/"
}

# Specific headers for Investorgain
INVESTORGAIN_HEADERS = {
    **COMMON_HEADERS,
    "Origin": "https://www.investorgain.com",
    "Referer": "https://www.investorgain.com/"
}
