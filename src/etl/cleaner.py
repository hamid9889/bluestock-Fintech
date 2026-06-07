import os
import pandas as pd
import numpy as np
from src.config import INPUT_DIR, RAW_DIR, PROCESSED_DAY2_DIR, API_MAP, OTHER_FILES

class DataCleaner:
    """Handles all data cleaning and standardization tasks."""

    def __init__(self):
        if not os.path.exists(PROCESSED_DAY2_DIR):
            os.makedirs(PROCESSED_DAY2_DIR)

    def save_processed(self, df: pd.DataFrame, filename: str):
        """Saves the cleaned dataframe to the processed directory."""
        output_path = os.path.join(PROCESSED_DAY2_DIR, f'day2_{filename}.csv')
        df.to_csv(output_path, index=False)
        print(f"Successfully processed and saved: {output_path}")

    def clean_nav_history(self):
        """Cleans and forward-fills the NAV history dataset."""
        print("Cleaning NAV History...")
        df = pd.read_csv(os.path.join(INPUT_DIR, '02_nav_history.csv'))
        df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
        df = df.dropna(subset=['date'])
        
        df = df.drop_duplicates(subset=['amfi_code', 'date'])
        df = df[df['nav'] > 0]
        df = df.sort_values(['amfi_code', 'date'])

        def _fill_missing_dates(group):
            if group.empty: return group
            date_range = pd.date_range(start=group['date'].min(), end=group['date'].max(), freq='D')
            group = group.set_index('date').reindex(date_range)
            group['nav'] = group['nav'].ffill()
            group['amfi_code'] = group['amfi_code'].ffill()
            return group.reset_index().rename(columns={'index': 'date'})

        # Group by amfi_code and apply forward fill for holidays
        df_cleaned = df.groupby('amfi_code', group_keys=False).apply(_fill_missing_dates)
        self.save_processed(df_cleaned, '02_nav_history_cleaning')

    def clean_investor_transactions(self):
        """Standardizes investor transactions and validates KYC status."""
        print("Cleaning Investor Transactions...")
        df = pd.read_csv(os.path.join(INPUT_DIR, '08_investor_transactions.csv'))
        df['transaction_date'] = pd.to_datetime(df['transaction_date'], dayfirst=True, errors='coerce')
        df = df.dropna(subset=['transaction_date'])
        
        type_mapping = {
            'SIP': 'SIP', 
            'Lumpsum': 'Lumpsum', 
            'Redemption': 'Redemption', 
            'STP': 'SIP', 
            'SWP': 'Redemption'
        }
        df['transaction_type'] = df['transaction_type'].map(lambda x: type_mapping.get(x, x))
        df = df[df['amount_inr'] > 0]
        
        valid_kyc_statuses = {'Verified', 'Pending', 'Rejected'}
        df['kyc_status'] = df['kyc_status'].apply(lambda x: x if x in valid_kyc_statuses else 'Pending')
        
        self.save_processed(df, '08_investor_transactions_cleaning')

    def clean_scheme_performance(self):
        """Validates performance metrics and flags expense ratio anomalies."""
        print("Cleaning Scheme Performance...")
        df = pd.read_csv(os.path.join(INPUT_DIR, '07_scheme_performance.csv'))
        
        return_columns = ['return_1yr_pct', 'return_3yr_pct', 'return_5yr_pct', 'benchmark_3yr_pct']
        for col in return_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
        df['expense_ratio_pct'] = pd.to_numeric(df['expense_ratio_pct'], errors='coerce')
        # Anomaly detection: expense ratio should ideally be between 0.1% and 2.5%
        df['expense_ratio_anomaly'] = ((df['expense_ratio_pct'] < 0.1) | (df['expense_ratio_pct'] > 2.5))
        
        self.save_processed(df, '07_scheme_performance_cleaning')

    def clean_api_data(self):
        """Processes raw NAV data fetched from APIs."""
        for name, amfi_code in API_MAP.items():
            print(f"Processing API data for: {name}...")
            file_path = os.path.join(RAW_DIR, f'nav_{amfi_code}.csv')
            if not os.path.exists(file_path):
                continue
                
            df = pd.read_csv(file_path)
            df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
            df = df.dropna(subset=['date'])
            
            if df.empty:
                print(f"Warning: No valid data found for {name}")
                continue

            df = df.drop_duplicates(subset=['date']).sort_values('date')
            df = df[df['nav'] > 0]
            
            if df.empty: continue

            # Reindex to fill missing dates
            date_range = pd.date_range(start=df['date'].min(), end=df['date'].max(), freq='D')
            df = df.set_index('date').reindex(date_range)
            df['nav'] = df['nav'].ffill()
            df['amfi_code'] = amfi_code
            df = df.reset_index().rename(columns={'index': 'date'})
            
            self.save_processed(df, f'api_{name}_cleaning')

    def clean_other_datasets(self):
        """Performs basic cleaning on all other CSV files."""
        for file_base in OTHER_FILES:
            print(f"Processing standard dataset: {file_base}...")
            df = pd.read_csv(os.path.join(INPUT_DIR, f'{file_base}.csv')).drop_duplicates()
            self.save_processed(df, f'{file_base}_cleaning')

    def run_all(self):
        """Executes the full cleaning pipeline."""
        self.clean_nav_history()
        self.clean_investor_transactions()
        self.clean_scheme_performance()
        self.clean_api_data()
        self.clean_other_datasets()
        print("\n--- All Data Cleaning Tasks Completed ---")
