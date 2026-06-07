import os
import pandas as pd
from sqlalchemy import create_engine, text
from src.config import DB_PATH, PROCESSED_DAY2_DIR, ANALYSIS_RESULTS_DIR

class DataAnalyzer:
    """Handles data extraction and analytical processing from the SQLite database."""

    def __init__(self):
        self.db_path = DB_PATH
        if not os.path.exists(ANALYSIS_RESULTS_DIR):
            os.makedirs(ANALYSIS_RESULTS_DIR)

    @property
    def engine(self):
        """Lazy initialization of the SQLAlchemy engine."""
        return create_engine(f'sqlite:///{self.db_path}')

    def save_analysis(self, df: pd.DataFrame, filename: str):
        """Saves analysis results to the specified output directory."""
        output_path = os.path.join(ANALYSIS_RESULTS_DIR, f'day3_{filename}.csv')
        df.to_csv(output_path, index=False)
        print(f"Analysis saved: {output_path}")

    def extract_nav_trends(self):
        print("Extracting NAV Trend Analysis Data...")
        query = """
            SELECT n.date, n.nav, f.scheme_name 
            FROM fact_nav n 
            JOIN dim_fund f ON n.amfi_code = f.amfi_code
        """
        df = pd.read_sql(query, self.engine)
        self.save_analysis(df, 'nav_trend_analysis')

    def extract_aum_growth(self):
        print("Extracting AUM Growth Analysis Data...")
        query = "SELECT fund_house, aum_crore, strftime('%Y', date) as year FROM fact_aum"
        df = pd.read_sql(query, self.engine)
        self.save_analysis(df, 'aum_growth_analysis')

    def extract_sip_inflows(self):
        print("Extracting SIP Inflow Time-series Data...")
        query = """
            SELECT d.year, d.month, SUM(t.amount_inr) as total_sip
            FROM fact_transactions t
            JOIN dim_date d ON t.transaction_date = d.date
            WHERE t.transaction_type = 'SIP'
            GROUP BY d.year, d.month
        """
        df = pd.read_sql(query, self.engine)
        self.save_analysis(df, 'sip_inflow_analysis')

    def extract_category_inflows(self):
        print("Extracting Category Inflow Analysis Data...")
        path = os.path.join(PROCESSED_DAY2_DIR, 'day2_05_category_inflows_cleaning.csv')
        df = pd.read_csv(path)
        self.save_analysis(df, 'category_inflow_analysis')

    def extract_investor_demographics(self):
        print("Extracting Investor Demographics...")
        query = """
            SELECT age_group, gender, COUNT(*) as investor_count, SUM(amount_inr) as total_amount 
            FROM fact_transactions 
            GROUP BY age_group, gender
        """
        df = pd.read_sql(query, self.engine)
        self.save_analysis(df, 'investor_demographics_analysis')

    def extract_geographic_distribution(self):
        print("Extracting Geographic Data...")
        query = """
            SELECT state, city_tier, SUM(amount_inr) as total_amount 
            FROM fact_transactions 
            GROUP BY state, city_tier
        """
        df = pd.read_sql(query, self.engine)
        self.save_analysis(df, 'geographic_distribution_analysis')

    def extract_folio_growth(self):
        print("Extracting Folio Growth Data...")
        path = os.path.join(PROCESSED_DAY2_DIR, 'day2_06_industry_folio_count_cleaning.csv')
        df = pd.read_csv(path)
        self.save_analysis(df, 'folio_growth_analysis')

    def extract_sector_allocation(self):
        print("Extracting Sector Allocation Data...")
        query = "SELECT sector, SUM(weight_pct) as total_weight FROM fact_portfolio_holdings GROUP BY sector ORDER BY total_weight DESC"
        df = pd.read_sql(query, self.engine)
        self.save_analysis(df, 'sector_allocation_analysis')

    def extract_folio_metrics(self):
        print("Extracting Detailed Folio Metrics...")
        query = "SELECT * FROM fact_folio_count"
        df = pd.read_sql(query, self.engine)
        self.save_analysis(df, 'folio_metrics_analysis')
        
    def extract_benchmark_data(self):
        print("Extracting Benchmark Index Data...")
        query = "SELECT * FROM fact_benchmark_indices"
        df = pd.read_sql(query, self.engine)
        self.save_analysis(df, 'benchmark_indices_analysis')

    def extract_returns_correlation(self):
        print("Extracting Returns Correlation Matrix...")
        with self.engine.connect() as conn:
            selected_amfi = pd.read_sql("SELECT amfi_code FROM dim_fund LIMIT 10", conn)['amfi_code'].tolist()
            amfi_list = ','.join(map(str, selected_amfi))
            query = f"SELECT date, nav, amfi_code FROM fact_nav WHERE amfi_code IN ({amfi_list})"
            df_raw = pd.read_sql(query, conn)
            
        df_pivot = df_raw.pivot(index='date', columns='amfi_code', values='nav')
        correlation_matrix = df_pivot.pct_change().corr().reset_index()
        self.save_analysis(correlation_matrix, 'returns_correlation_analysis')

    def run_all(self):
        """Executes the full analytical pipeline."""
        self.extract_nav_trends()
        self.extract_aum_growth()
        self.extract_sip_inflows()
        self.extract_category_inflows()
        self.extract_investor_demographics()
        self.extract_geographic_distribution()
        self.extract_sector_allocation()
        self.extract_folio_metrics()
        self.extract_benchmark_data()
        self.extract_returns_correlation()
        print("\n--- All Analytical Tasks Completed ---")
