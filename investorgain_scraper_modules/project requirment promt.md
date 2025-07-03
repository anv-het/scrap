read under this folder all the files aswell as. those all files scrap data from the nvestorgain vis scraping and this data i save in to jason file with perticuler files. 

so i scrap data succesfully from the investorgain and cretaed section wise a data sxript file bur also in to this file i have a same data repitatly mulipule times right, so this things also we have to handle this.

This project aims to create a robust Python application that leverages your existing scraping scripts to gather comprehensive IPO data and then store this consolidated information into a structured database.

for the evsry file output we have jason formate.

1. The Python script 01_get_ipo_name.py is designed to extract specific information about Initial Public Offerings (IPOs) from the Investorgain website. Its primary goal is to collect company names and their associated logos. The process begins by fetching a list of IPOs using an API endpoint. Subsequently, the script iterates through each IPO entry. For every IPO, it constructs a unique URL to access its detailed webpage. On this detail page, the script utilizes web scraping techniques to parse the HTML content and pinpoint the company's name and the URL of its logo. The script also includes a feature to optionally download these logos and store them locally. Finally, all the collected data—comprising the IPO ID, the company name (both as provided by the API and as scraped from the webpage), the IPO category, the detail page URL, the company logo URL, and the local path if the logo was downloaded—is compiled and saved into a JSON file. A summary of the scraping operation is then provided.

2. The Python script 02_get_ipo_details.py is designed to perform a more in-depth scraping of IPO (Initial Public Offering) details from the Investorgain website, building upon the initial IPO list obtained from an API. It fetches a list of IPOs and then navigates to each IPO's dedicated detail page. On these pages, the script extracts comprehensive information such as the company's full name, an "About Company" text, and various IPO-specific details like issue price, type, size, fresh issue, face value, promoter holdings (pre and post-IPO), and key dates (opening and closing). It also attempts to extract the number of shares per lot from the IPO summary text. The script processes dates to determine if an IPO is past, present, or future. All the collected and parsed data is then consolidated and saved into a structured JSON file, and a summary of the scraping operation, including counts of upcoming, ongoing, and completed IPOs, is printed.

3. 03_get_ipo_important_dates.py: This script focuses on extracting critical dates related to IPOs, such as the opening and closing dates, basis of allotment, initiation of refunds, credit of shares to Demat accounts, and listing dates. It parses these dates from IPO detail pages and categorizes IPOs by their date status (past, present, or future).

4. 04_get_ipo_lots.py: This script is designed to extract details about IPO lot sizes, including the number of shares and the amount required for retail and HNI (High Net Worth Individual) investors. It navigates to each IPO's detail page after fetching the IPO list from an API, specifically targeting tables containing lot information.

5. 05_get_ipo_gmp.py: This script scrapes the Grey Market Premium (GMP) data for IPOs. It fetches the latest GMP values and historical trends for each IPO by accessing a specific API endpoint that provides this information. It also includes robust error handling for API responses and data decompression.

6. 06_get_about_company.py: This script focuses on extracting the "About Company" text for each IPO from their respective detail pages. It identifies and consolidates multiple paragraphs related to the company's description, providing a comprehensive overview.

7. 07_get_ipo_strengths.py: This script is built to extract the strengths of each company undergoing an IPO. It fetches these points from the IPO detail pages, typically listed as bullet points or within specific sections, providing insights into the company's competitive advantages.

8. 09_get_ipo_objective.py: This script extracts the objectives of the IPO, detailing how the company intends to use the proceeds from the public offering. It retrieves this information from the IPO detail pages, often presented as a list or a paragraph.

9. 10_get_live_subscription_summary.py: This script is dedicated to fetching live subscription data for IPOs. It retrieves information on how many times an IPO has been subscribed by different investor categories (e.g., QIB, NII, Retail) and may also get day-wise subscription trends and share allocation details from a specific subscription API.

10. 12_get_company_financials.py: This script scrapes the financial statements of companies going public. It targets tables containing financial data (e.g., balance sheets, profit & loss statements) from the IPO detail pages and organizes this information, often in a structured format like a Pandas DataFrame, before saving it.

11. 13_get_ipo_peer_comparison.py: This script focuses on extracting peer comparison data for IPOs. It identifies and scrapes tables that compare the IPO-bound company's financials and key metrics with those of its listed industry peers, providing a comparative analysis.

12. 14_get_contact_management_details.py: This script extracts contact and management details related to the IPO, including the company's address, IPO registrar information, and details of the lead managers involved in the IPO process. It parses these details from dedicated sections on the IPO detail pages.

13. The Python script 15_get_last_updated.py is designed to extract the "Last Updated on" date and time from a given webpage's HTML content. It employs multiple methods to locate this information: first, by searching within div elements with specific classes, then by looking for the phrase "Last Updated on" within any <p> tags, and finally, as a fallback, by attempting to find a date and time string matching a specific regular expression pattern anywhere in the page's text. If the information is found, it is returned; otherwise, it indicates that the information was not found or an error occurred during the extraction process.

THE UPPER ALL THE DETAILES ABOUT THE MY WOLE FILES I CRETATED FOR THE SCRAP ALL THE DATA ABOUT IPO . 

Here is a prompt explaining all the uploaded files and their output to an AI:

"This is a collection of Python scripts designed to scrape detailed information about Initial Public Offerings (IPOs) from the Investorgain website. Each script focuses on a specific aspect of IPO data and outputs its findings into a JSON file.

01_get_ipo_name.py: This script scrapes company names and their logos from IPO detail pages. It outputs the data, including IPO IDs, API and scraped company names, IPO categories, detail URLs, logo URLs, and local logo paths (if downloaded), into a JSON file named company_names_logos.json.

02_get_ipo_details.py: This script extracts comprehensive IPO details such as the company's full name, "About Company" text, issue price, type, size, fresh issue, face value, promoter holdings, and key dates. It saves this information as a structured JSON file.

03_get_ipo_important_dates.py: This script specifically focuses on extracting and categorizing all important IPO dates, including open/close dates, allotment, refunds, Demat credit, and listing dates. The output is stored in a JSON file, typically named ipo_important_dates.json.

04_get_ipo_lots.py: This script is responsible for scraping IPO lot size details for retail and HNI investors, including shares per lot and the amount required. The extracted lot information is saved into a JSON file.

05_get_ipo_gmp.py: This script retrieves Grey Market Premium (GMP) data for IPOs, including current values and historical trends, from a specific API endpoint. The collected GMP data is saved to a JSON file, often named ipo_gmp_data.json.

06_get_about_company.py: This script extracts the extensive "About Company" description for each IPO from their detail pages. The full text is then stored in a JSON file.

07_get_ipo_strengths.py: This script extracts and compiles the identified strengths of companies undergoing IPOs, usually presented as bullet points on their detail pages. This data is outputted into a JSON file, such as ipo_strengths_detailed.json.

09_get_ipo_objective.py: This script extracts the stated objectives for each IPO, outlining how the company plans to utilize the funds raised. This information is then saved into a JSON file, often included within a broader IPO details file.

10_get_live_subscription_summary.py: This script fetches live IPO subscription data, including subscription rates by investor category and day-wise bidding history. This dynamic data is saved to a JSON file.

12_get_company_financials.py: This script is designed to scrape detailed financial statements (e.g., balance sheets, profit & loss) for the companies. The structured financial data is saved into a JSON file.

13_get_ipo_peer_comparison.py: This script extracts comparative financial and metric data between the IPO-bound company and its industry peers. The peer comparison data is stored in a JSON file.

14_get_contact_management_details.py: This script extracts contact information, IPO registrar details, and lead manager information for each IPO. This structured data is stored in a JSON file.

15_get_last_updated.py: This script specifically extracts the "Last Updated on" date and time from a webpage, using multiple parsing methods. While it doesn't create a separate output file for this information directly, it's typically used to capture a timestamp that might be integrated into the JSON output of other scraping scripts."


Project Overview: Comprehensive IPO Data Collection and Database Storage:
The core objective of this project is to build an automated system that collects a wide array of IPO-related data from Investorgain.com, integrates it, and persists it into a relational database. This will provide a centralized, queryable source of truth for all scraped IPO information.

Project Architecture and Components
   1. Data Sources (Your Existing Python Scrapers):

    01_get_ipo_name.py: Provides basic IPO names, short names, and logo URLs.

    02_get_ipo_details.py: Extracts comprehensive IPO details like company full name, "About Company" text, issue size, price band, and key dates.

    03_get_ipo_important_dates.py: Specifically focuses on all important IPO dates (open, close, allotment, listing, etc.) and their status.

    04_get_ipo_lots.py: Scrapes detailed IPO lot information for various investor categories.

    05_get_ipo_gmp.py: Fetches Grey Market Premium (GMP) data, including current values and historical trends.

    06_get_about_company.py: Extracts the detailed "About Company" narrative.

    07_get_ipo_strengths.py: Gathers the identified strengths of the IPO company.

    09_get_ipo_objective.py: Extracts the objectives for which IPO funds will be used.

    10_get_live_subscription_summary.py: Collects live IPO subscription data, including category-wise bids and day-wise trends.

    12_get_company_financials.py: Scrapes the company's financial statements.

    13_get_ipo_peer_comparison.py: Extracts data comparing the IPO company with its industry peers.

    14_get_contact_management_details.py: Retrieves contact details, registrar, and lead manager information.

    15_get_last_updated.py: A utility to get the last updated timestamp of a page, which can be integrated into the overall record.

    2. Orchestration and Data Integration Layer (New Main Script):



End-to-End Project Flow:
Initialization:

The main orchestration script starts.

It establishes a connection to the chosen database.

Fetch Initial IPO List:

The script first calls fetch_ipo_list_from_api() (from 01_get_ipo_name.py or 02_get_ipo_details.py as it's common) to get a list of all current and upcoming IPOs with their basic identifiers (like IPO ID, company_short_name, urlrewrite_folder_name). This list will serve as the master list of IPOs to process.

Iterative Detailed Scraping and Merging:

For each IPO in the master list:

The script constructs the detail URL for that specific IPO.

It then sequentially calls the relevant functions from all other scraping scripts (extract_company_about, extract_ipo_important_dates, scrape_ipo_lots_table, fetch_gmp_data_for_ipo, fetch_ipo_subscription_data, scrape_and_format_financial_data, scrape_peer_comparison, extract_contact_sections, etc.), passing the necessary URL or IPO ID.

As data is returned from each scraper, the orchestration layer will merge it into a single, comprehensive dictionary or object for the current IPO, using the IPO ID as the unique identifier to combine records. This involves:

Adding new fields: If a scraper provides unique data (e.g., GMP trend table), it's added.

Updating/Overwriting fields: If a scraper provides more detailed or accurate data for an existing field (e.g., a more complete company name than the API provides), it updates the existing value.

Handling nested structures: Data like financial tables, GMP trends, or subscription breakdowns (which are lists of dictionaries) will be stored as JSON strings within a single database column if the table design is flat, or in separate child tables if a normalized schema is preferred.

Data Cleaning and Transformation:

Before insertion, the merged data will undergo final cleaning and type conversion (e.g., ensuring all numeric values are stored as numbers, dates as date objects, and large text blocks are properly escaped for database insertion).

Database Insertion/Update:

Once all data for a single IPO is collected, merged, and cleaned, the orchestration script will insert this comprehensive record into the designated database table.

If an IPO record already exists (e.g., during a re-run to update live data), the script will perform an UPDATE operation instead of an INSERT.

Error Handling and Logging:

Throughout the process, robust try-except blocks will be implemented to catch network errors, parsing errors, and database errors.

Detailed logs will be generated to track the progress of scraping, identify which IPOs were processed successfully, and pinpoint any errors or skipped items.

Concurrency (already present in some scripts):

For efficiency, the main script can leverage ThreadPoolExecutor (as seen in 07_get_ipo_strengths.py and 12_get_company_financials.py) to scrape multiple IPO detail pages concurrently, significantly speeding up the data collection process.

Conceptual Database Table Design (Example - Single Table Approach)
While the final table design is TBD, here's a conceptual representation of how a single, wide table could store this data, demonstrating the integration:

Table Name: ipo_master_data

Column Name

Data Type

Description

Source Script(s)

ipo_id

INT

Unique identifier for the IPO (Primary Key)

All

company_short_name_api

VARCHAR

Short name from API list

01, 02, 03, 04, 05, 10

company_full_name_scraped

VARCHAR

Full company name scraped from detail page

01, 02, 06

ipo_category

VARCHAR

IPO category (Mainboard, SME, etc.)

01, 02, 03, 04

detail_url

VARCHAR

URL of the IPO detail page

All

scraping_date

DATETIME

Timestamp of when the data was last scraped

All (added by orchestration)

ipo_open_date

DATE

IPO opening date

02, 03

ipo_close_date

DATE

IPO closing date

02, 03

listing_date

DATE

IPO listing date

02, 03

basis_of_allotment_date

DATE

Date for basis of allotment

03

refunds_initiation_date

DATE

Date for initiation of refunds

03

credit_shares_demat_date

DATE

Date for credit of shares to Demat account

03

ipo_open_date_status

VARCHAR

Status of IPO open date (Past, Today, Future, Unknown)

02, 03

ipo_close_date_status

VARCHAR

Status of IPO close date (Past, Today, Future, Unknown)

02, 03

listing_date_status

VARCHAR

Status of IPO listing date (Past, Today, Future, Unknown)

02, 03

about_company_text

TEXT

Detailed "About Company" description

02, 06

issue_price_band

VARCHAR

IPO issue price range

02, 04

issue_size_cr

DECIMAL

Total issue size in Crores

02, 04

shares_per_lot

INT

Number of shares per lot

02, 04

min_order_quantity

VARCHAR

Minimum order quantity (e.g., "1 lot")

02, 04

gmp_latest

DECIMAL

Latest Grey Market Premium value

05

estimated_listing_price

DECIMAL

Estimated listing price based on GMP

05

gmp_trend_history_json

JSONB/TEXT

Historical GMP trend data (JSON array of objects)

05

ipo_strengths_json

JSONB/TEXT

List of company strengths (JSON array of strings)

07, 09

ipo_objectives_json

JSONB/TEXT

List of IPO objectives (JSON array of objects)

09

subscription_bidding_history_json

JSONB/TEXT

Detailed IPO bidding data (JSON array of objects)

10

subscription_share_allocation_json

JSONB/TEXT

IPO share allocation details (JSON array of objects)

10

subscription_daywise_table_json

JSONB/TEXT

Day-wise subscription data (JSON array of objects)

10

company_financials_json

JSONB/TEXT

Restated consolidated financial information (JSON array of objects)

12

peer_comparison_json

JSONB/TEXT

Peer comparison data (JSON array of objects)

13

contact_company_address_json

JSONB/TEXT

Company address details (JSON object)

14

contact_ipo_registrar_json

JSONB/TEXT

IPO Registrar details (JSON object)

14

contact_ipo_lead_manager_json

1. i want to create this proper project with utilits,
2. run with single main.py file run projet, 
3. project for the scrap from the invetergain site, 
4. that project also include data save in to database.
5. well stucred project that can ave  utilits and db connections models and all things.


we want to save data into db as of now currenatly we save data in to local sqlite3 db then we will save data in to mssql