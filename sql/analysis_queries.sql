-- ====================================================================
-- Finomaly: Advanced SQL Analytical Queries
-- Demonstrating CTEs, Window Functions, Rolling Aggregations & Financial KPIs
-- ====================================================================

-- --------------------------------------------------------------------
-- QUERY 1: Monthly Financial Performance & Savings Rate
-- --------------------------------------------------------------------
SELECT 
    year_month,
    ROUND(SUM(CASE WHEN transaction_type = 'Income' THEN amount ELSE 0 END), 2) AS income,
    ROUND(SUM(CASE WHEN transaction_type = 'Expense' THEN amount ELSE 0 END), 2) AS expense,
    ROUND(SUM(CASE WHEN transaction_type = 'Income' THEN amount ELSE 0 END) - 
          SUM(CASE WHEN transaction_type = 'Expense' THEN amount ELSE 0 END), 2) AS net_cashflow,
    ROUND(
        (SUM(CASE WHEN transaction_type = 'Income' THEN amount ELSE 0 END) - 
         SUM(CASE WHEN transaction_type = 'Expense' THEN amount ELSE 0 END)) / 
        NULLIF(SUM(CASE WHEN transaction_type = 'Income' THEN amount ELSE 0 END), 0) * 100, 
        2
    ) AS savings_rate_pct
FROM transactions
GROUP BY year_month
ORDER BY year_month DESC;


-- --------------------------------------------------------------------
-- QUERY 2: Month-over-Month (MoM) Category Spend & Velocity (Window LAG)
-- --------------------------------------------------------------------
WITH MonthlyCategorySpend AS (
    SELECT 
        year_month,
        category,
        ROUND(SUM(amount), 2) AS current_spend
    FROM transactions
    WHERE transaction_type = 'Expense'
    GROUP BY year_month, category
),
SpendWithLag AS (
    SELECT 
        year_month,
        category,
        current_spend,
        LAG(current_spend, 1) OVER (
            PARTITION BY category 
            ORDER BY year_month
        ) AS prior_month_spend
    FROM MonthlyCategorySpend
)
SELECT 
    year_month,
    category,
    current_spend,
    COALESCE(prior_month_spend, 0) AS prior_month_spend,
    ROUND(current_spend - prior_month_spend, 2) AS mom_dollar_change,
    ROUND(((current_spend - prior_month_spend) / NULLIF(prior_month_spend, 0)) * 100, 1) AS mom_growth_pct
FROM SpendWithLag
WHERE prior_month_spend IS NOT NULL
ORDER BY year_month DESC, mom_dollar_change DESC;


-- --------------------------------------------------------------------
-- QUERY 3: Pareto 80/20 Analysis on Merchants
-- Identifies the vital few merchants driving the vast majority of outlays
-- --------------------------------------------------------------------
WITH MerchantTotals AS (
    SELECT 
        clean_merchant,
        category,
        ROUND(SUM(amount), 2) AS merchant_spend,
        COUNT(*) AS transaction_count
    FROM transactions
    WHERE transaction_type = 'Expense'
    GROUP BY clean_merchant, category
),
MerchantCumulative AS (
    SELECT 
        clean_merchant,
        category,
        merchant_spend,
        transaction_count,
        SUM(merchant_spend) OVER (ORDER BY merchant_spend DESC) AS running_total_spend,
        SUM(merchant_spend) OVER () AS grand_total_spend
    FROM MerchantTotals
)
SELECT 
    clean_merchant,
    category,
    merchant_spend,
    transaction_count,
    ROUND((running_total_spend / grand_total_spend) * 100, 2) AS cumulative_spend_pct,
    CASE 
        WHEN (running_total_spend / grand_total_spend) <= 0.80 THEN 'Top 80% Spend (Vital Few)'
        ELSE 'Long Tail (Trivial Many)'
    END AS pareto_tier
FROM MerchantCumulative
ORDER BY merchant_spend DESC;


-- --------------------------------------------------------------------
-- QUERY 4: 7-Day Rolling Moving Average of Daily Variable Spending
-- Smooths day-to-day volatility to detect spending trajectory
-- --------------------------------------------------------------------
WITH DailySpend AS (
    SELECT 
        date,
        ROUND(SUM(amount), 2) AS daily_spend
    FROM transactions
    WHERE transaction_type = 'Expense'
    GROUP BY date
)
SELECT 
    date,
    daily_spend,
    ROUND(AVG(daily_spend) OVER (
        ORDER BY date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ), 2) AS rolling_7day_avg_spend
FROM DailySpend
ORDER BY date DESC
LIMIT 60;


-- --------------------------------------------------------------------
-- QUERY 5: 50 / 30 / 20 Budget Benchmark Audit
-- Compares actual allocation (Needs vs Wants vs Savings) to ideal standard
-- --------------------------------------------------------------------
WITH MonthlyBuckets AS (
    SELECT 
        year_month,
        ROUND(SUM(CASE WHEN budget_bucket = 'Needs' AND transaction_type = 'Expense' THEN amount ELSE 0 END), 2) AS needs_spend,
        ROUND(SUM(CASE WHEN budget_bucket = 'Wants' AND transaction_type = 'Expense' THEN amount ELSE 0 END), 2) AS wants_spend,
        ROUND(SUM(CASE WHEN budget_bucket = 'Savings' OR transaction_type = 'Transfer' THEN amount ELSE 0 END), 2) AS savings_alloc,
        ROUND(SUM(CASE WHEN transaction_type = 'Income' THEN amount ELSE 0 END), 2) AS total_income
    FROM transactions
    GROUP BY year_month
)
SELECT 
    year_month,
    total_income,
    needs_spend,
    ROUND((needs_spend / NULLIF(total_income, 0)) * 100, 1) AS needs_pct,
    wants_spend,
    ROUND((wants_spend / NULLIF(total_income, 0)) * 100, 1) AS wants_pct,
    savings_alloc,
    ROUND((savings_alloc / NULLIF(total_income, 0)) * 100, 1) AS savings_pct,
    CASE 
        WHEN (needs_spend / NULLIF(total_income, 0)) > 0.50 THEN 'Over Needs Target'
        ELSE 'Healthy Needs'
    END AS needs_status,
    CASE 
        WHEN (wants_spend / NULLIF(total_income, 0)) > 0.30 THEN 'Over Discretionary Target'
        ELSE 'Disciplined Wants'
    END AS wants_status
FROM MonthlyBuckets
WHERE total_income > 0
ORDER BY year_month DESC;


-- --------------------------------------------------------------------
-- QUERY 6: Subscription & Recurring Cost Leakage Audit
-- Aggregates monthly recurring expenses and projects annual run-rate
-- --------------------------------------------------------------------
SELECT 
    clean_merchant,
    category,
    subcategory,
    COUNT(DISTINCT year_month) AS active_months_count,
    ROUND(AVG(amount), 2) AS avg_monthly_charge,
    ROUND(SUM(amount), 2) AS total_lifetime_paid,
    ROUND(AVG(amount) * 12, 2) AS projected_annual_cost
FROM transactions
WHERE is_recurring = 1 AND transaction_type = 'Expense'
GROUP BY clean_merchant, category, subcategory
ORDER BY projected_annual_cost DESC;


-- --------------------------------------------------------------------
-- QUERY 7: Weekend vs. Weekday Behavioral Heatmap
-- Analyzes discretionary spending bias by day of the week
-- --------------------------------------------------------------------
SELECT 
    day_name,
    is_weekend,
    COUNT(*) AS total_transactions,
    ROUND(SUM(amount), 2) AS total_spend,
    ROUND(AVG(amount), 2) AS avg_ticket_size,
    ROUND(SUM(CASE WHEN budget_bucket = 'Wants' THEN amount ELSE 0 END), 2) AS discretionary_spend,
    ROUND(
        SUM(CASE WHEN budget_bucket = 'Wants' THEN amount ELSE 0 END) / 
        NULLIF(SUM(amount), 0) * 100, 
        1
    ) AS discretionary_ratio_pct
FROM transactions
WHERE transaction_type = 'Expense'
GROUP BY day_name, is_weekend
ORDER BY total_spend DESC;


-- --------------------------------------------------------------------
-- QUERY 8: Budget vs. Actual Variance Analysis
-- Evaluates performance against monthly budgeted spending limits
-- --------------------------------------------------------------------
WITH ActualSpend AS (
    SELECT 
        category,
        ROUND(AVG(monthly_total), 2) AS avg_actual_monthly_spend
    FROM (
        SELECT 
            year_month,
            category,
            SUM(amount) AS monthly_total
        FROM transactions
        WHERE transaction_type = 'Expense'
        GROUP BY year_month, category
    )
    GROUP BY category
)
SELECT 
    b.category,
    b.budget_bucket,
    b.monthly_budget_target,
    COALESCE(a.avg_actual_monthly_spend, 0) AS avg_actual_monthly_spend,
    ROUND(COALESCE(a.avg_actual_monthly_spend, 0) - b.monthly_budget_target, 2) AS monthly_variance,
    ROUND(
        ((COALESCE(a.avg_actual_monthly_spend, 0) - b.monthly_budget_target) / 
        b.monthly_budget_target) * 100, 
        1
    ) AS variance_pct,
    CASE 
        WHEN COALESCE(a.avg_actual_monthly_spend, 0) > b.monthly_budget_target THEN 'Over Budget (Overspending)'
        ELSE 'Under Budget (Surplus)'
    END AS budget_status
FROM budgets b
LEFT JOIN ActualSpend a ON b.category = a.category
ORDER BY monthly_variance DESC;
