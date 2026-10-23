"""
Finomaly - ETL & Data Processing Pipeline
Extracts raw banking feeds, cleans strings, handles nulls, engineers temporal & financial features,
and loads structured records into both CSV and a SQLite Analytical Data Warehouse.
"""

import os
import re
import sqlite3
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
SQL_SCHEMA_PATH = os.path.join(BASE_DIR, "sql", "schema.sql")
DB_PATH = os.path.join(PROCESSED_DIR, "spendsense.db")

def extract_data():
    """Extract raw transaction and lookup files."""
    print("[1/4] Extracting raw datasets from data/raw...")
    raw_tx_path = os.path.join(RAW_DIR, "raw_transactions.csv")
    accounts_path = os.path.join(RAW_DIR, "accounts.csv")
    budgets_path = os.path.join(RAW_DIR, "monthly_budgets.csv")

    if not os.path.exists(raw_tx_path):
        raise FileNotFoundError(f"Missing raw transactions file: {raw_tx_path}")

    df_tx = pd.read_csv(raw_tx_path)
    df_accounts = pd.read_csv(accounts_path)
    df_budgets = pd.read_csv(budgets_path)
    print(f"      Loaded {len(df_tx):,} raw transactions, {len(df_accounts)} accounts, {len(df_budgets)} budget categories.")
    return df_tx, df_accounts, df_budgets

def transform_data(df_tx, df_accounts, df_budgets):
    """Clean, impute missing values, and engineer temporal/financial features."""
    print("[2/4] Transforming and cleaning data...")
    df = df_tx.copy()

    # 1. Null handling & string sanitization
    nulls_before = df.isnull().sum().to_dict()
    df["city"] = df["city"].fillna("Online / Unknown").str.strip().str.title()
    df["state"] = df["state"].fillna("US").str.strip().str.upper()
    df["raw_description"] = df["raw_description"].str.strip().str.upper()
    df["clean_merchant"] = df["clean_merchant"].str.strip()

    # 2. Date parsing and temporal features
    df["date"] = pd.to_datetime(df["date"])
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["year_month"] = df["date"].dt.strftime("%Y-%m")
    df["day_name"] = df["date"].dt.day_name()
    df["is_weekend"] = df["date"].dt.weekday.apply(lambda x: 1 if x >= 5 else 0)
    df["quarter"] = df["date"].dt.to_period("Q").astype(str)

    # 3. Numeric sanitation & precision
    df["amount"] = df["amount"].round(2)
    df["is_recurring"] = df["is_recurring"].astype(int)

    # 4. Outlier & High Value Tagging
    expense_mask = df["transaction_type"] == "Expense"
    p95 = df.loc[expense_mask, "amount"].quantile(0.95)
    df["is_high_value"] = ((df["amount"] >= p95) & expense_mask).astype(int)

    # Sort deterministically by date and ID
    df = df.sort_values(by=["date", "transaction_id"]).reset_index(drop=True)
    # Convert date back to standard string for SQLite/CSV compatibility
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")

    print(f"      Nulls handled: {nulls_before}")
    print(f"      Temporal features added: year, month, year_month, day_name, is_weekend, quarter.")
    print(f"      High-value spend threshold (95th percentile): ${p95:.2f}")
    return df, df_accounts, df_budgets

def load_data(df_tx, df_accounts, df_budgets):
    """Save cleaned datasets to CSV and populate SQLite database."""
    print("[3/4] Loading processed data into CSV & SQLite warehouse...")
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    # Save to clean CSV
    clean_csv_path = os.path.join(PROCESSED_DIR, "clean_transactions.csv")
    df_tx.to_csv(clean_csv_path, index=False)
    print(f"      Clean CSV saved: {clean_csv_path}")

    # Initialize SQLite Database using schema
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if os.path.exists(SQL_SCHEMA_PATH):
        with open(SQL_SCHEMA_PATH, "r") as f:
            schema_script = f.read()
        cursor.executescript(schema_script)
        conn.commit()

    # Load Accounts
    df_accounts.to_sql("accounts", conn, if_exists="replace", index=False)
    # Load Budgets
    df_budgets.to_sql("budgets", conn, if_exists="replace", index=False)
    
    # Selected columns matching SQL schema
    schema_cols = [
        "transaction_id", "date", "account_id", "raw_description", "clean_merchant",
        "amount", "transaction_type", "category", "subcategory", "budget_bucket",
        "is_recurring", "payment_channel", "city", "state", "year", "month",
        "year_month", "day_name", "is_weekend"
    ]
    df_tx[schema_cols].to_sql("transactions", conn, if_exists="append", index=False)
    conn.commit()
    conn.close()

    print(f"      SQLite database populated: {DB_PATH}")

def run_pipeline_validation():
    """Verify integrity of loaded database."""
    print("[4/4] Validating database integrity...")
    conn = sqlite3.connect(DB_PATH)
    
    total_tx = pd.read_sql_query("SELECT COUNT(*) as count FROM transactions;", conn).iloc[0]["count"]
    total_spend = pd.read_sql_query("SELECT ROUND(SUM(amount), 2) as spend FROM transactions WHERE transaction_type='Expense';", conn).iloc[0]["spend"]
    total_income = pd.read_sql_query("SELECT ROUND(SUM(amount), 2) as income FROM transactions WHERE transaction_type='Income';", conn).iloc[0]["income"]
    months_count = pd.read_sql_query("SELECT COUNT(DISTINCT year_month) as months FROM transactions;", conn).iloc[0]["months"]
    
    conn.close()

    print(f"      [OK] Total Transactions In DB: {total_tx:,}")
    print(f"      [OK] Total Recorded Spend:    ${total_spend:,.2f}")
    print(f"      [OK] Total Recorded Income:   ${total_income:,.2f}")
    print(f"      [OK] Reporting Periods:       {months_count} months")
    print("[SUCCESS] Finomaly ETL Pipeline completed successfully!")

if __name__ == "__main__":
    raw_tx, raw_acc, raw_bud = extract_data()
    clean_tx, clean_acc, clean_bud = transform_data(raw_tx, raw_acc, raw_bud)
    load_data(clean_tx, clean_acc, clean_bud)
    run_pipeline_validation()
