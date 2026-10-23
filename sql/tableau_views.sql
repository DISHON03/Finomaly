-- ====================================================================
-- Finomaly — Tableau Reporting SQL Views
-- Designed for direct ODBC connection from Tableau Desktop / Tableau Prep
-- ====================================================================

-- 1. View: Monthly Cash Flow & 50/30/20 Compliance
CREATE VIEW IF NOT EXISTS v_tableau_monthly_summary AS
SELECT 
    SUBSTR(date, 1, 7) AS year_month,
    ROUND(SUM(CASE WHEN transaction_type = 'Income' THEN amount ELSE 0 END), 2) AS total_income,
    ROUND(SUM(CASE WHEN transaction_type = 'Expense' THEN amount ELSE 0 END), 2) AS total_expense,
    ROUND(SUM(CASE WHEN transaction_type = 'Income' THEN amount ELSE 0 END) - 
          SUM(CASE WHEN transaction_type = 'Expense' THEN amount ELSE 0 END), 2) AS net_cashflow,
    ROUND((SUM(CASE WHEN transaction_type = 'Income' THEN amount ELSE 0 END) - 
           SUM(CASE WHEN transaction_type = 'Expense' THEN amount ELSE 0 END)) / 
           NULLIF(SUM(CASE WHEN transaction_type = 'Income' THEN amount ELSE 0 END), 0) * 100, 2) AS savings_rate_pct,
    ROUND(SUM(CASE WHEN budget_bucket = 'Needs' AND transaction_type = 'Expense' THEN amount ELSE 0 END), 2) AS needs_spend,
    ROUND(SUM(CASE WHEN budget_bucket = 'Wants' AND transaction_type = 'Expense' THEN amount ELSE 0 END), 2) AS wants_spend,
    ROUND(SUM(CASE WHEN budget_bucket = 'Needs' AND transaction_type = 'Expense' THEN amount ELSE 0 END) / 
          NULLIF(SUM(CASE WHEN transaction_type = 'Income' THEN amount ELSE 0 END), 0) * 100, 1) AS needs_pct,
    ROUND(SUM(CASE WHEN budget_bucket = 'Wants' AND transaction_type = 'Expense' THEN amount ELSE 0 END) / 
          NULLIF(SUM(CASE WHEN transaction_type = 'Income' THEN amount ELSE 0 END), 0) * 100, 1) AS wants_pct,
    ROUND((SUM(CASE WHEN transaction_type = 'Income' THEN amount ELSE 0 END) - 
           SUM(CASE WHEN transaction_type = 'Expense' THEN amount ELSE 0 END)) / 
           NULLIF(SUM(CASE WHEN transaction_type = 'Income' THEN amount ELSE 0 END), 0) * 100, 1) AS savings_pct
FROM transactions
GROUP BY SUBSTR(date, 1, 7)
ORDER BY year_month ASC;

-- 2. View: Category Spend & Proportion of Wallet
CREATE VIEW IF NOT EXISTS v_tableau_category_spend AS
SELECT 
    category,
    budget_bucket,
    ROUND(SUM(amount), 2) AS total_spend,
    COUNT(*) AS transaction_count,
    ROUND(AVG(amount), 2) AS avg_ticket_size,
    ROUND(SUM(amount) / (SELECT SUM(amount) FROM transactions WHERE transaction_type = 'Expense') * 100, 2) AS pct_of_total_spend
FROM transactions
WHERE transaction_type = 'Expense'
GROUP BY category, budget_bucket
ORDER BY total_spend DESC;

-- 3. View: Budget Variance & Utilization
CREATE VIEW IF NOT EXISTS v_tableau_budget_variance AS
SELECT 
    b.category,
    b.budget_bucket,
    b.monthly_target,
    COALESCE(ROUND(s.actual_spent, 2), 0.0) AS actual_spent,
    ROUND(b.monthly_target - COALESCE(s.actual_spent, 0.0), 2) AS remaining_budget,
    ROUND(COALESCE(s.actual_spent, 0.0) / NULLIF(b.monthly_target, 0) * 100, 1) AS utilization_pct,
    CASE 
        WHEN COALESCE(s.actual_spent, 0.0) > b.monthly_target THEN 'EXCEEDED'
        WHEN (COALESCE(s.actual_spent, 0.0) / NULLIF(b.monthly_target, 0) * 100) >= b.alert_threshold THEN 'APPROACHING'
        ELSE 'HEALTHY'
    END AS performance_status
FROM budgets b
LEFT JOIN (
    SELECT category, SUM(amount) AS actual_spent
    FROM transactions
    WHERE transaction_type = 'Expense'
      AND SUBSTR(date, 1, 7) = (SELECT MAX(SUBSTR(date, 1, 7)) FROM transactions)
    GROUP BY category
) s ON b.category = s.category;

-- 4. View: Active Spending Anomalies & Explanations
CREATE VIEW IF NOT EXISTS v_tableau_anomalies AS
SELECT 
    a.id AS alert_id,
    COALESCE(t.date, SUBSTR(a.created_at, 1, 10)) AS date,
    COALESCE(t.clean_merchant, 'Category Aggregate') AS clean_merchant,
    COALESCE(t.amount, 0.0) AS amount,
    COALESCE(t.category, a.title) AS category,
    a.alert_type,
    a.severity,
    a.comparison_metric,
    a.difference_amount,
    a.status,
    a.explanation
FROM anomaly_alerts a
LEFT JOIN transactions t ON a.transaction_id = t.id
ORDER BY a.created_at DESC;
