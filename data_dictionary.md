# Data Dictionary - Bluestock Fintech Mutual Fund Database

## Dimension Tables

### 1. `dim_fund`
Stores metadata about mutual fund schemes.
- `amfi_code` (PK): Unique identification code for the scheme.
- `scheme_name`: Full name of the mutual fund scheme.
- `fund_house`: Asset Management Company (AMC) name.
- `category`: Category of the fund (e.g., Large Cap, Mid Cap, Gilt).
- `plan`: Type of plan (Direct or Regular).

### 2. `dim_date`
Calendar dimension for time-series analysis.
- `date` (PK): Date in YYYY-MM-DD format.
- `day`: Day of the month.
- `month`: Month number.
- `year`: Year.
- `quarter`: Quarter of the year (1-4).
- `day_of_week`: Name of the day (e.g., Monday).

## Fact Tables

### 3. `fact_nav`
Stores historical Net Asset Value (NAV) data.
- `nav_id` (PK): Auto-incrementing ID.
- `amfi_code` (FK): Reference to `dim_fund`.
- `date` (FK): Reference to `dim_date`.
- `nav`: Net Asset Value on that date.

### 4. `fact_transactions`
Stores investor transaction records.
- `transaction_id` (PK): Auto-incrementing ID.
- `investor_id`: Unique ID for the investor.
- `transaction_date` (FK): Date of transaction.
- `amfi_code` (FK): Reference to `dim_fund`.
- `transaction_type`: Type of transaction (SIP, Lumpsum, Redemption).
- `amount_inr`: Transaction amount in Indian Rupees.
- `state`: State of the investor.
- `city`: City of the investor.
- `city_tier`: Tier of the city (e.g., T30, B30).
- `age_group`: Age bracket of the investor.
- `gender`: Gender of the investor.
- `annual_income_lakh`: Annual income in Lakhs.
- `payment_mode`: Mode of payment (UPI, Cheque, Mandate).
- `kyc_status`: Status of KYC (Verified, Pending, Rejected).

### 5. `fact_performance`
Stores performance metrics and risk ratios for funds.
- `performance_id` (PK): Auto-incrementing ID.
- `amfi_code` (FK): Reference to `dim_fund`.
- `return_1yr_pct`: 1-year trailing returns.
- `return_3yr_pct`: 3-year trailing returns.
- `return_5yr_pct`: 5-year trailing returns.
- `benchmark_3yr_pct`: Benchmark's 3-year returns.
- `alpha`: Excess return over the benchmark.
- `beta`: Volatility relative to the market/benchmark.
- `sharpe_ratio`: Risk-adjusted return.
- `sortino_ratio`: Downside risk-adjusted return.
- `std_dev_ann_pct`: Annualized standard deviation.
- `max_drawdown_pct`: Maximum peak-to-trough decline.
- `aum_crore`: Assets Under Management in Crores.
- `expense_ratio_pct`: Annual fee charged by the fund.
- `morningstar_rating`: Star rating (1-5).
- `risk_grade`: Risk level (e.g., Low, Moderate, High, Very High).
- `expense_ratio_anomaly`: Boolean flag for expense ratios outside 0.1% - 2.5%.

### 6. `fact_aum`
Stores historical AUM data for fund houses.
- `aum_id` (PK): Auto-incrementing ID.
- `fund_house`: Name of the fund house.
- `aum_crore`: Total AUM in Crores.
- `date` (FK): Date of recording.
