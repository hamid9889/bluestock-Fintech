-- queries.sql
-- 10 Analytical SQL Queries for Bluestock Fintech

-- 1. Top 5 funds by AUM
SELECT scheme_name, aum_crore 
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
ORDER BY aum_crore DESC 
LIMIT 5;

-- 2. Average NAV per month for a specific fund (e.g., AMFI 119551)
SELECT d.year, d.month, AVG(n.nav) as avg_nav
FROM fact_nav n
JOIN dim_date d ON n.date = d.date
WHERE n.amfi_code = 119551
GROUP BY d.year, d.month
ORDER BY d.year, d.month;

-- 3. SIP Year-over-Year (YoY) growth in transaction amount
WITH YearlySIP AS (
    SELECT d.year, SUM(amount_inr) as total_sip
    FROM fact_transactions t
    JOIN dim_date d ON t.transaction_date = d.date
    WHERE t.transaction_type = 'SIP'
    GROUP BY d.year
)
SELECT curr.year, curr.total_sip, 
       ((curr.total_sip - prev.total_sip) * 100.0 / prev.total_sip) as yoy_growth_pct
FROM YearlySIP curr
LEFT JOIN YearlySIP prev ON curr.year = prev.year + 1;

-- 4. Total transaction amount by State
SELECT state, SUM(amount_inr) as total_amount
FROM fact_transactions
GROUP BY state
ORDER BY total_amount DESC;

-- 5. Funds with expense ratio less than 1%
SELECT scheme_name, expense_ratio_pct
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
WHERE expense_ratio_pct < 1.0;

-- 6. Top 5 Cities by number of investors (unique investor_id)
SELECT city, COUNT(DISTINCT investor_id) as investor_count
FROM fact_transactions
GROUP BY city
ORDER BY investor_count DESC
LIMIT 5;

-- 7. Distribution of transactions by Age Group
SELECT age_group, COUNT(*) as transaction_count, SUM(amount_inr) as total_amount
FROM fact_transactions
GROUP BY age_group
ORDER BY total_amount DESC;

-- 8. Average Alpha and Beta by Category
SELECT f.category, AVG(p.alpha) as avg_alpha, AVG(p.beta) as avg_beta
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
GROUP BY f.category;

-- 9. Transaction count by Payment Mode
SELECT payment_mode, COUNT(*) as count
FROM fact_transactions
GROUP BY payment_mode;

-- 10. Funds with the highest Morningstar Rating (5) and their 3-year returns
SELECT scheme_name, return_3yr_pct, morningstar_rating
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
WHERE morningstar_rating = 5
ORDER BY return_3yr_pct DESC;
