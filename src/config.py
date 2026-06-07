import os

# Base directory
BASE_DIR = r'c:\Users\Dell\OneDrive\Desktop\task 1'

# Data Directories
INPUT_DIR = os.path.join(BASE_DIR, 'data', 'csv_upload')
RAW_DIR = os.path.join(BASE_DIR, 'data', 'raw')
PROCESSED_DAY2_DIR = os.path.join(BASE_DIR, 'data', 'day2_processed')
ANALYSIS_RESULTS_DIR = os.path.join(BASE_DIR, 'data', 'day3_analysis_results')

# Database
DB_PATH = os.path.join(BASE_DIR, 'bluestock_mf.db')
SCHEMA_PATH = os.path.join(BASE_DIR, 'sql', 'schema.sql')

# API Configuration
API_MAP = {
    "01_hdfc": "125497",
    "02_sbi": "119551",
    "03_icici": "120503",
    "04_nippon": "118632",
    "05_axis": "119092",
    "06_kotak": "120841"
}

# List of other CSV files to process
OTHER_FILES = [
    "01_fund_master",
    "03_aum_by_fund_house",
    "04_monthly_sip_inflows",
    "05_category_inflows",
    "06_industry_folio_count",
    "09_portfolio_holdings",
    "10_benchmark_indices"
]
