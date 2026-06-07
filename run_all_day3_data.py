import pandas as pd
import numpy as np
import os
from sqlalchemy import create_engine, text

# Paths
db_path = r'c:\Users\Dell\OneDrive\Desktop\task 1\bluestock_mf.db'
processed_dir = r'c:\Users\Dell\OneDrive\Desktop\task 1\data\day2_processed'
output_dir = r'c:\Users\Dell\OneDrive\Desktop\task 1\data\day3_analysis_results'

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

engine = create_engine(f'sqlite:///{db_path}')

def save_analysis(df, filename):
    df.to_csv(os.path.join(output_dir, f'day3_{filename}.csv'), index=False)
    print(f"Saved: day3_{filename}.csv")

# 1. NAV Trend Data
print("Extracting NAV Trend Data...")
query_nav = "SELECT n.date, n.nav, f.scheme_name FROM fact_nav n JOIN dim_fund f ON n.amfi_code = f.amfi_code"
df_nav = pd.read_sql(query_nav, engine)
save_analysis(df_nav, 'nav_trend_analysis')

# 2. AUM Growth Data
print("Extracting AUM Growth Data...")
query_aum = "SELECT fund_house, aum_crore, strftime('%Y', date) as year FROM fact_aum"
df_aum = pd.read_sql(query_aum, engine)
save_analysis(df_aum, 'aum_growth_analysis')

# 3. SIP Inflow Time-series Data
print("Extracting SIP Inflow Data...")
query_sip = """
SELECT d.year, d.month, SUM(t.amount_inr) as total_sip
FROM fact_transactions t
JOIN dim_date d ON t.transaction_date = d.date
WHERE t.transaction_type = 'SIP'
GROUP BY d.year, d.month
"""
df_sip = pd.read_sql(query_sip, engine)
save_analysis(df_sip, 'sip_inflow_analysis')

# 4. Category Inflow Data
print("Extracting Category Inflow Data...")
df_cat = pd.read_csv(os.path.join(processed_dir, 'day2_05_category_inflows_cleaning.csv'))
save_analysis(df_cat, 'category_inflow_analysis')

# 5. Investor Demographics Data (Age & Gender)
print("Extracting Investor Demographics...")
query_demo = "SELECT age_group, gender, COUNT(*) as investor_count, SUM(amount_inr) as total_amount FROM fact_transactions GROUP BY age_group, gender"
df_demo = pd.read_sql(query_demo, engine)
save_analysis(df_demo, 'investor_demographics_analysis')

# 6. Geographic Distribution (State & City Tier)
print("Extracting Geographic Data...")
query_geo = "SELECT state, city_tier, SUM(amount_inr) as total_amount FROM fact_transactions GROUP BY state, city_tier"
df_geo = pd.read_sql(query_geo, engine)
save_analysis(df_geo, 'geographic_distribution_analysis')

# 7. Folio Count Growth Data
print("Extracting Folio Growth Data...")
df_folio = pd.read_csv(os.path.join(processed_dir, 'day2_06_industry_folio_count_cleaning.csv'))
save_analysis(df_folio, 'folio_growth_analysis')

# 8. Sector Allocation Data
print("Extracting Sector Allocation Data...")
df_holdings = pd.read_csv(os.path.join(processed_dir, 'day2_09_portfolio_holdings_cleaning.csv'))
sector_summary = df_holdings.groupby('sector')['weight_pct'].sum().reset_index().sort_values('weight_pct', ascending=False)
save_analysis(sector_summary, 'sector_allocation_analysis')

# 9. Correlation Matrix Data
print("Extracting Correlation Data...")
# Get daily returns for top 10 funds
selected_amfi = pd.read_sql("SELECT amfi_code FROM dim_fund LIMIT 10", engine)['amfi_code'].tolist()
query_corr = f"SELECT date, nav, amfi_code FROM fact_nav WHERE amfi_code IN ({','.join(map(str, selected_amfi))})"
df_corr_raw = pd.read_sql(query_corr, engine)
df_pivot = df_corr_raw.pivot(index='date', columns='amfi_code', values='nav')
df_returns_corr = df_pivot.pct_change().corr().reset_index()
save_analysis(df_returns_corr, 'returns_correlation_analysis')

print("\nAll Day 3 analysis data collected and saved in data/day3_analysis_results/")
