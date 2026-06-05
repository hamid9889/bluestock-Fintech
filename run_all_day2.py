import pandas as pd
import numpy as np
import os
import glob

# Paths
input_dir = r'c:\Users\Dell\OneDrive\Desktop\task 1\data\csv_upload'
raw_dir = r'c:\Users\Dell\OneDrive\Desktop\task 1\data\raw'
output_dir = r'c:\Users\Dell\OneDrive\Desktop\task 1\data\day2_processed'

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def clean_and_save(df, filename):
    df.to_csv(os.path.join(output_dir, f'day2_{filename}.csv'), index=False)
    print(f"Saved: day2_{filename}.csv")

# 1. 02_nav_history
print("Processing 02_nav_history...")
df = pd.read_csv(os.path.join(input_dir, '02_nav_history.csv'))
df['date'] = pd.to_datetime(df['date'])
df = df.drop_duplicates(subset=['amfi_code', 'date'])
df = df[df['nav'] > 0]
df = df.sort_values(['amfi_code', 'date'])
def fill_dates(group):
    min_date = group['date'].min()
    max_date = group['date'].max()
    all_dates = pd.date_range(start=min_date, end=max_date, freq='D')
    group = group.set_index('date').reindex(all_dates)
    group['nav'] = group['nav'].ffill()
    group['amfi_code'] = group['amfi_code'].ffill()
    return group.reset_index().rename(columns={'index': 'date'})
df_nav = df.groupby('amfi_code', group_keys=False).apply(fill_dates)
clean_and_save(df_nav, '02_nav_history_cleaning')

# 2. 08_investor_transactions
print("Processing 08_investor_transactions...")
df = pd.read_csv(os.path.join(input_dir, '08_investor_transactions.csv'))
df['transaction_date'] = pd.to_datetime(df['transaction_date'])
type_map = {'SIP': 'SIP', 'Lumpsum': 'Lumpsum', 'Redemption': 'Redemption', 'STP': 'SIP', 'SWP': 'Redemption'}
df['transaction_type'] = df['transaction_type'].map(lambda x: type_map.get(x, x))
df = df[df['amount_inr'] > 0]
valid_kyc = ['Verified', 'Pending', 'Rejected']
df['kyc_status'] = df['kyc_status'].apply(lambda x: x if x in valid_kyc else 'Pending')
clean_and_save(df, '08_investor_transactions_cleaning')

# 3. 07_scheme_performance
print("Processing 07_scheme_performance...")
df = pd.read_csv(os.path.join(input_dir, '07_scheme_performance.csv'))
return_cols = ['return_1yr_pct', 'return_3yr_pct', 'return_5yr_pct', 'benchmark_3yr_pct']
for col in return_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')
df['expense_ratio_pct'] = pd.to_numeric(df['expense_ratio_pct'], errors='coerce')
df['expense_ratio_anomaly'] = ((df['expense_ratio_pct'] < 0.1) | (df['expense_ratio_pct'] > 2.5))
clean_and_save(df, '07_scheme_performance_cleaning')

# 4. API Files
api_map = {"01_hdfc": "125497", "02_sbi": "119551", "03_icici": "120503", "04_nippon": "118632", "05_axis": "119092", "06_kotak": "120841"}
for key, amfi in api_map.items():
    print(f"Processing API: {key}...")
    df = pd.read_csv(os.path.join(raw_dir, f'nav_{amfi}.csv'))
    df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
    df = df.drop_duplicates(subset=['date']).sort_values('date')
    df = df[df['nav'] > 0]
    all_dates = pd.date_range(start=df['date'].min(), end=df['date'].max(), freq='D')
    df = df.set_index('date').reindex(all_dates)
    df['nav'] = df['nav'].ffill()
    df['amfi_code'] = amfi
    df = df.reset_index().rename(columns={'index': 'date'})
    clean_and_save(df, f'api_{key}_cleaning')

# 5. Other CSVs
other_files = ["01_fund_master", "03_aum_by_fund_house", "04_monthly_sip_inflows", "05_category_inflows", "06_industry_folio_count", "09_portfolio_holdings", "10_benchmark_indices"]
for f in other_files:
    print(f"Processing: {f}...")
    df = pd.read_csv(os.path.join(input_dir, f'{f}.csv')).drop_duplicates()
    clean_and_save(df, f'{f}_cleaning')

print("\nAll Day 2 processing complete!")
