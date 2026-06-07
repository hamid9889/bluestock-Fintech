import os
import sqlite3
import pandas as pd
from sqlalchemy import create_engine, text
from src.config import DB_PATH, SCHEMA_PATH, PROCESSED_DAY2_DIR

class DataLoader:
    """Handles the creation of the SQLite database and loading of cleaned datasets."""

    def __init__(self):
        self.engine = create_engine(f'sqlite:///{DB_PATH}')

    def initialize_database(self):
        """Creates the database and applies the star schema."""
        print(f"Initializing database at: {DB_PATH}")
        
        # Try to remove the old database file if it exists
        if os.path.exists(DB_PATH):
            try:
                # Close any existing engine connections
                self.engine.dispose()
                os.remove(DB_PATH)
                print("Old database file removed.")
            except Exception as e:
                print(f"Warning: Could not remove old database file ({e}). Attempting to drop tables instead.")
                # Fallback: Just drop all tables if file is locked
                with self.engine.connect() as conn:
                    conn.execute(text("PRAGMA foreign_keys = OFF;"))
                    # Get all table names
                    tables = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';")).fetchall()
                    for table in tables:
                        if table[0] != 'sqlite_sequence':
                            conn.execute(text(f"DROP TABLE IF EXISTS {table[0]};"))
                    conn.execute(text("PRAGMA foreign_keys = ON;"))
                    conn.commit()
            
        conn = sqlite3.connect(DB_PATH)
        with open(SCHEMA_PATH, 'r') as f:
            schema_sql = f.read()
        conn.executescript(schema_sql)
        conn.close()
        print("Schema applied successfully.")

    def load_table(self, csv_filename: str, table_name: str, columns: list = None):
        """Loads a specific CSV file into a database table."""
        path = os.path.join(PROCESSED_DAY2_DIR, csv_filename)
        if not os.path.exists(path):
            print(f"Warning: File {path} not found. Skipping table {table_name}.")
            return

        df = pd.read_csv(path)
        if columns:
            df = df[columns]
            
        df.to_sql(table_name, self.engine, if_exists='append', index=False)
        print(f"Loaded {len(df)} rows into {table_name}.")

    def run_all(self):
        """Orchestrates the full database loading process."""
        self.initialize_database()

        # 1. Dimensions (MUST BE LOADED FIRST)
        print("Loading Dimensions...")
        # Load dim_fund from performance data
        self.load_table('day2_07_scheme_performance_cleaning.csv', 'dim_fund', 
                        ['amfi_code', 'scheme_name', 'fund_house', 'category', 'plan'])

        # 2. Generate and load dim_date (Required for fact tables)
        print("Generating and loading dim_date...")
        df_nav = pd.read_csv(os.path.join(PROCESSED_DAY2_DIR, 'day2_02_nav_history_cleaning.csv'))
        df_trans = pd.read_csv(os.path.join(PROCESSED_DAY2_DIR, 'day2_08_investor_transactions_cleaning.csv'))
        
        # Combine all dates from relevant tables
        all_dates = pd.concat([df_nav['date'], df_trans['transaction_date']]).unique()
        
        dim_date = pd.DataFrame({'date': all_dates})
        dim_date['date'] = pd.to_datetime(dim_date['date'])
        dim_date = dim_date.dropna(subset=['date']) # Ensure no invalid dates
        
        dim_date['day'] = dim_date['date'].dt.day
        dim_date['month'] = dim_date['date'].dt.month
        dim_date['year'] = dim_date['date'].dt.year
        dim_date['quarter'] = dim_date['date'].dt.quarter
        dim_date['day_of_week'] = dim_date['date'].dt.day_name()
        dim_date['date'] = dim_date['date'].dt.strftime('%Y-%m-%d')
        
        dim_date.to_sql('dim_date', self.engine, if_exists='append', index=False)
        print(f"Loaded {len(dim_date)} dates into dim_date.")

        # 3. Fact Tables
        print("Loading Fact Tables...")
        self.load_table('day2_02_nav_history_cleaning.csv', 'fact_nav')
        self.load_table('day2_08_investor_transactions_cleaning.csv', 'fact_transactions')
        
        performance_cols = [
            'amfi_code', 'return_1yr_pct', 'return_3yr_pct', 'return_5yr_pct', 
            'benchmark_3yr_pct', 'alpha', 'beta', 'sharpe_ratio', 'sortino_ratio', 
            'std_dev_ann_pct', 'max_drawdown_pct', 'aum_crore', 'expense_ratio_pct', 
            'morningstar_rating', 'risk_grade', 'expense_ratio_anomaly'
        ]
        self.load_table('day2_07_scheme_performance_cleaning.csv', 'fact_performance', performance_cols)
        self.load_table('day2_03_aum_by_fund_house_cleaning.csv', 'fact_aum', ['fund_house', 'aum_crore', 'date'])
        
        # 4. Additional Tables
        print("Loading Additional Datasets...")
        self.load_table('day2_05_category_inflows_cleaning.csv', 'fact_category_inflows')
        self.load_table('day2_06_industry_folio_count_cleaning.csv', 'fact_folio_count')
        self.load_table('day2_09_portfolio_holdings_cleaning.csv', 'fact_portfolio_holdings')
        self.load_table('day2_10_benchmark_indices_cleaning.csv', 'fact_benchmark_indices')

        print("\n--- All Data Loading Tasks Completed ---")
