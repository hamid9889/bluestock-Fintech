import pandas as pd
import sqlite3
import os
from sqlalchemy import create_engine

# Paths
processed_dir = r'c:\Users\Dell\OneDrive\Desktop\task 1\data\processed'
db_path = r'c:\Users\Dell\OneDrive\Desktop\task 1\bluestock_mf.db'
schema_path = r'c:\Users\Dell\OneDrive\Desktop\task 1\sql\schema.sql'

def load_data():
    # 1. Create SQLite database and apply schema
    print("Initializing database and applying schema...")
    conn = sqlite3.connect(db_path)
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)
    conn.close()

    engine = create_engine(f'sqlite:///{db_path}')

    # 2. Load dim_fund from scheme_performance_cleaned
    print("Loading dim_fund...")
    df_perf = pd.read_csv(os.path.join(processed_dir, 'scheme_performance_cleaned.csv'))
    dim_fund = df_perf[['amfi_code', 'scheme_name', 'fund_house', 'category', 'plan']].drop_duplicates()
    dim_fund.to_sql('dim_fund', engine, if_exists='append', index=False)

    # 3. Load fact_nav
    print("Loading fact_nav...")
    df_nav = pd.read_csv(os.path.join(processed_dir, 'nav_history_cleaned.csv'))
    df_nav.to_sql('fact_nav', engine, if_exists='append', index=False)

    # 4. Load fact_transactions
    print("Loading fact_transactions...")
    df_trans = pd.read_csv(os.path.join(processed_dir, 'investor_transactions_cleaned.csv'))
    df_trans.to_sql('fact_transactions', engine, if_exists='append', index=False)

    # 5. Load fact_performance
    print("Loading fact_performance...")
    # Select only columns that exist in the schema
    fact_perf_cols = [
        'amfi_code', 'return_1yr_pct', 'return_3yr_pct', 'return_5yr_pct', 
        'benchmark_3yr_pct', 'alpha', 'beta', 'sharpe_ratio', 'sortino_ratio', 
        'std_dev_ann_pct', 'max_drawdown_pct', 'aum_crore', 'expense_ratio_pct', 
        'morningstar_rating', 'risk_grade', 'expense_ratio_anomaly'
    ]
    df_perf_fact = df_perf[fact_perf_cols]
    df_perf_fact.to_sql('fact_performance', engine, if_exists='append', index=False)

    # 6. Load dim_date (from all dates in nav and transactions)
    print("Loading dim_date...")
    all_dates = pd.concat([df_nav['date'], df_trans['transaction_date']]).unique()
    dim_date = pd.DataFrame({'date': all_dates})
    dim_date['date'] = pd.to_datetime(dim_date['date'])
    dim_date['day'] = dim_date['date'].dt.day
    dim_date['month'] = dim_date['date'].dt.month
    dim_date['year'] = dim_date['date'].dt.year
    dim_date['quarter'] = dim_date['date'].dt.quarter
    dim_date['day_of_week'] = dim_date['date'].dt.day_name()
    dim_date['date'] = dim_date['date'].dt.strftime('%Y-%m-%d')
    dim_date.to_sql('dim_date', engine, if_exists='append', index=False)

    # 7. Load fact_aum
    print("Loading fact_aum...")
    df_aum = pd.read_csv(os.path.join(processed_dir, 'aum_by_fund_house_cleaned.csv'))
    # Select only columns that exist in the schema
    fact_aum_cols = ['fund_house', 'aum_crore', 'date']
    df_aum_fact = df_aum[fact_aum_cols]
    df_aum_fact.to_sql('fact_aum', engine, if_exists='append', index=False)

    # Verify counts
    print("\nVerification (Row Counts):")
    from sqlalchemy import text
    with engine.connect() as conn:
        for table in ['dim_fund', 'dim_date', 'fact_nav', 'fact_transactions', 'fact_performance']:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            print(f"{table}: {count}")

if __name__ == "__main__":
    load_data()
