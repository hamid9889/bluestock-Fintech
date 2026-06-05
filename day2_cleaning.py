import pandas as pd
import numpy as np
import os
from sqlalchemy import create_engine

# Paths
input_dir = r'c:\Users\Dell\OneDrive\Desktop\task 1\data\csv_upload'
output_dir = r'c:\Users\Dell\OneDrive\Desktop\task 1\data\processed'

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def clean_nav_history():
    print("Cleaning nav_history.csv...")
    df = pd.read_csv(os.path.join(input_dir, '02_nav_history.csv'))
    
    # 1. Parse dates to datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # 2. Sort by amfi_code + date
    df = df.sort_values(['amfi_code', 'date'])
    
    # 3. Remove duplicates
    df = df.drop_duplicates(subset=['amfi_code', 'date'])
    
    # 4. Validate NAV > 0
    df = df[df['nav'] > 0]
    
    # 5. Forward-fill missing NAV for holidays/weekends
    # Create a full date range for each amfi_code
    def fill_dates(group):
        min_date = group['date'].min()
        max_date = group['date'].max()
        all_dates = pd.date_range(start=min_date, end=max_date, freq='D')
        group = group.set_index('date').reindex(all_dates)
        group['nav'] = group['nav'].ffill()
        group['amfi_code'] = group['amfi_code'].ffill()
        group.index.name = 'date'
        return group.reset_index()

    df = df.groupby('amfi_code').apply(fill_dates).reset_index(drop=True)
    
    df.to_csv(os.path.join(output_dir, 'nav_history_cleaned.csv'), index=False)
    return df

def clean_investor_transactions():
    print("Cleaning investor_transactions.csv...")
    df = pd.read_csv(os.path.join(input_dir, '08_investor_transactions.csv'))
    
    # 1. Fix date formats
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    
    # 2. Standardise transaction_type values
    type_map = {
        'SIP': 'SIP',
        'Lumpsum': 'Lumpsum',
        'Redemption': 'Redemption',
        'STP': 'SIP', # Mapping others if any
        'SWP': 'Redemption'
    }
    df['transaction_type'] = df['transaction_type'].map(lambda x: type_map.get(x, x))
    
    # 3. Validate amount > 0
    df = df[df['amount_inr'] > 0]
    
    # 4. Check KYC status enum values
    valid_kyc = ['Verified', 'Pending', 'Rejected']
    df['kyc_status'] = df['kyc_status'].apply(lambda x: x if x in valid_kyc else 'Pending')
    
    df.to_csv(os.path.join(output_dir, 'investor_transactions_cleaned.csv'), index=False)
    return df

def clean_scheme_performance():
    print("Cleaning scheme_performance.csv...")
    df = pd.read_csv(os.path.join(input_dir, '07_scheme_performance.csv'))
    
    # 1. Validate all return values are numeric
    return_cols = ['return_1yr_pct', 'return_3yr_pct', 'return_5yr_pct', 'benchmark_3yr_pct']
    for col in return_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 2. Check expense_ratio range (0.1% – 2.5%)
    df['expense_ratio_pct'] = pd.to_numeric(df['expense_ratio_pct'], errors='coerce')
    # Flag anomalies (out of range)
    df['expense_ratio_anomaly'] = ((df['expense_ratio_pct'] < 0.1) | (df['expense_ratio_pct'] > 2.5))
    
    df.to_csv(os.path.join(output_dir, 'scheme_performance_cleaned.csv'), index=False)
    return df

def clean_others():
    # Cleaning other files and saving to processed
    files = [
        '01_fund_master.csv', '03_aum_by_fund_house.csv', '04_monthly_sip_inflows.csv',
        '05_category_inflows.csv', '06_industry_folio_count.csv', '09_portfolio_holdings.csv',
        '10_benchmark_indices.csv'
    ]
    for file in files:
        print(f"Copying {file} to processed...")
        df = pd.read_csv(os.path.join(input_dir, file))
        new_name = file.split('_', 1)[1].replace('.csv', '_cleaned.csv')
        df.to_csv(os.path.join(output_dir, new_name), index=False)

if __name__ == "__main__":
    clean_nav_history()
    clean_investor_transactions()
    clean_scheme_performance()
    clean_others()
    print("All datasets cleaned and saved to data/processed/")
