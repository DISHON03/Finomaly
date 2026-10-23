-- ====================================================================
-- Finomaly Database Schema (SQLite)
-- Designed for Personal Financial Analytics, Budgeting & Cash Flow Modeling
-- ====================================================================

DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS budgets;
DROP TABLE IF EXISTS accounts;

-- Accounts Table
CREATE TABLE accounts (
    account_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('Checking', 'Savings', 'Credit Card', 'Investment'))
);

-- Budgets Table
CREATE TABLE budgets (
    category TEXT PRIMARY KEY,
    budget_bucket TEXT NOT NULL,
    monthly_budget_target REAL NOT NULL
);

-- Transactions Table
CREATE TABLE transactions (
    transaction_id TEXT PRIMARY KEY,
    date TEXT NOT NULL,
    account_id TEXT NOT NULL,
    raw_description TEXT NOT NULL,
    clean_merchant TEXT NOT NULL,
    amount REAL NOT NULL,
    transaction_type TEXT NOT NULL CHECK(transaction_type IN ('Expense', 'Income', 'Transfer')),
    category TEXT NOT NULL,
    subcategory TEXT NOT NULL,
    budget_bucket TEXT NOT NULL,
    is_recurring INTEGER DEFAULT 0,
    payment_channel TEXT,
    city TEXT,
    state TEXT,
    year INTEGER,
    month INTEGER,
    year_month TEXT,
    day_name TEXT,
    is_weekend INTEGER,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id)
);

-- Indices for rapid analytical slicing
CREATE INDEX idx_tx_date ON transactions(date);
CREATE INDEX idx_tx_year_month ON transactions(year_month);
CREATE INDEX idx_tx_category ON transactions(category);
CREATE INDEX idx_tx_type ON transactions(transaction_type);
CREATE INDEX idx_tx_account ON transactions(account_id);

-- View: Monthly Cash Flow Summary
CREATE VIEW IF NOT EXISTS v_monthly_cashflow AS
SELECT 
    year_month,
    ROUND(SUM(CASE WHEN transaction_type = 'Income' THEN amount ELSE 0 END), 2) AS total_income,
    ROUND(SUM(CASE WHEN transaction_type = 'Expense' THEN amount ELSE 0 END), 2) AS total_expense,
    ROUND(SUM(CASE WHEN transaction_type = 'Transfer' THEN amount ELSE 0 END), 2) AS total_transfers,
    ROUND(SUM(CASE WHEN transaction_type = 'Income' THEN amount ELSE 0 END) - 
          SUM(CASE WHEN transaction_type = 'Expense' THEN amount ELSE 0 END), 2) AS net_cashflow,
    ROUND((SUM(CASE WHEN transaction_type = 'Income' THEN amount ELSE 0 END) - 
           SUM(CASE WHEN transaction_type = 'Expense' THEN amount ELSE 0 END)) / 
           NULLIF(SUM(CASE WHEN transaction_type = 'Income' THEN amount ELSE 0 END), 0) * 100, 2) AS savings_rate_pct
FROM transactions
GROUP BY year_month
ORDER BY year_month ASC;

-- View: Monthly Budget Compliance (50/30/20 Rule)
CREATE VIEW IF NOT EXISTS v_50_30_20_compliance AS
SELECT
    year_month,
    ROUND(SUM(CASE WHEN budget_bucket = 'Needs' AND transaction_type = 'Expense' THEN amount ELSE 0 END), 2) AS needs_spend,
    ROUND(SUM(CASE WHEN budget_bucket = 'Wants' AND transaction_type = 'Expense' THEN amount ELSE 0 END), 2) AS wants_spend,
    ROUND(SUM(CASE WHEN budget_bucket = 'Savings' OR transaction_type = 'Transfer' THEN amount ELSE 0 END), 2) AS savings_alloc,
    ROUND(SUM(CASE WHEN transaction_type = 'Income' THEN amount ELSE 0 END), 2) AS monthly_income,
    ROUND(SUM(CASE WHEN budget_bucket = 'Needs' AND transaction_type = 'Expense' THEN amount ELSE 0 END) / 
          NULLIF(SUM(CASE WHEN transaction_type = 'Income' THEN amount ELSE 0 END), 0) * 100, 1) AS needs_pct,
    ROUND(SUM(CASE WHEN budget_bucket = 'Wants' AND transaction_type = 'Expense' THEN amount ELSE 0 END) / 
          NULLIF(SUM(CASE WHEN transaction_type = 'Income' THEN amount ELSE 0 END), 0) * 100, 1) AS wants_pct,
    ROUND(SUM(CASE WHEN budget_bucket = 'Savings' OR transaction_type = 'Transfer' THEN amount ELSE 0 END) / 
          NULLIF(SUM(CASE WHEN transaction_type = 'Income' THEN amount ELSE 0 END), 0) * 100, 1) AS savings_pct
FROM transactions
GROUP BY year_month
ORDER BY year_month ASC;
