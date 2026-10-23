# 💳 Finomaly: Intelligent Expense Analytics & Anomaly Detection

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Database](https://img.shields.io/badge/Database-SQLite-003B57.svg)](https://sqlite.org/)
[![Dashboard](https://img.shields.io/badge/Dashboard-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![Visualizations](https://img.shields.io/badge/Visuals-Plotly%20%7C%20Seaborn-blueviolet.svg)](https://plotly.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **Understand Your Spending. Detect the Unusual.**  
> An end-to-end Data Analytics, Business Intelligence & Predictive Modeling platform for personal cash flow optimization, 50/30/20 budget auditing, subscription leakage detection, machine learning anomaly detection, and spend velocity forecasting.

---

## 📌 Project Overview
Personal cash flow management suffers from **spending opacity**: consumers lack clear visibility into discretionary leakage, subscription creep, and seasonal expenditure volatility.

**Finomaly** solves this by delivering an automated, production-grade analytics pipeline:
- Ingests raw, multi-account banking & credit card transaction feeds.
- Normalizes messy merchant strings, handles nulls, and engineers temporal/financial features.
- Persists structured data into a relational SQLite database warehouse (`spendsense.db`).
- Runs advanced SQL analytical queries (CTEs, Window Functions `LAG()`, Rolling Averages, Pareto Cumulative Sums).
- Surfaces insights through an interactive **React + Vite / Tailwind** modern web application, **Streamlit & Plotly** executive dashboard, and a comprehensive **Jupyter Notebook**.

---

## 🏛️ System Architecture

```
                  RAW INGESTION
          ┌───────────────────────────┐
          │ • Checking (ACH / Payroll)│
          │ • Credit Cards (Amex/Chase│
          │ • Savings (Ally HYSA)     │
          └─────────────┬─────────────┘
                        │
                        ▼
                  ETL PIPELINE (src/etl_pipeline.py)
          ┌───────────────────────────┐
          │ • Regex String Cleaning   │
          │ • Null Imputation         │
          │ • Date & Temporal Features│
          │ • 95th Percentile Outliers│
          └─────────────┬─────────────┘
                        │
                        ▼
               ANALYTICAL STORAGE
          ┌───────────────────────────┐
          │ • clean_transactions.csv  │
          │ • SQLite DB (spendsense)  │
          └─────────────┬─────────────┘
                        │
         ┌──────────────┴──────────────┐
         ▼                             ▼
   ADVANCED SQL (sql/)         STREAMLIT APP (app/)
  • Window Functions LAG()    • Executive KPI Cards
  • Pareto 80/20 Cum. Sum     • 50/30/20 Compliance
  • 7-Day Rolling Averages    • Holt's Trend Forecast
  • Budget Variance CTEs      • What-If Simulator
```

---

## 📂 Repository Structure

```text
Finomaly/
├── app/
│   └── app.py                     # Streamlit interactive analytics dashboard
├── data/
│   ├── raw/                       # Raw uncleaned transaction and metadata feeds
│   └── processed/                 # Cleaned CSV & SQLite database (spendsense.db)
├── notebooks/
│   └── Finomaly_EDA_and_Insights.ipynb   # End-to-end EDA, statistics & visualizations
├── reports/
│   └── EXECUTIVE_SUMMARY.md       # C-suite executive briefing with findings & recommendations
├── sql/
│   ├── schema.sql                 # DDL schema definitions, tables, indices, and views
│   └── analysis_queries.sql       # Advanced SQL queries (CTEs, Window functions, Pareto)
├── src/
│   ├── generate_data.py           # Realistic synthetic multi-year transaction generator
│   ├── etl_pipeline.py            # Automated ETL and data warehouse loader
│   ├── analysis.py                # Core statistical metrics, KPIs & IQR anomaly detector
│   └── forecast.py                # Holt's Linear Trend forecasting & runway calculator
├── requirements.txt               # Python package dependencies
└── README.md                      # Comprehensive project documentation
```

---

## 📊 Key Business Discoveries

1. **Pareto 80/20 Rule on Vendors:**
   * **Top 18 merchants drive 81.3% of total expenditures**. Housing (rent) and core utilities are the largest fixed components, while dining delivery and retail account for the bulk of discretionary variance.
2. **Weekend Spending Surge:**
   * Transactions on Friday–Sunday carry an **average ticket size of $84.20**, compared to **$46.10 on weekdays** (+82.6% spike), primarily propelled by restaurants and delivery apps.
3. **Subscription Leakage & Creep:**
   * 9 active recurring subscriptions were detected, amounting to **$3,420.24 in annualized commitment**. 4 redundant video streaming subscriptions were identified.
4. **50/30/20 Budget Rule Compliance:**
   * **Needs:** 48.2% (Target: ≤ 50%) — *Compliant*
   * **Wants:** 38.4% (Target: ≤ 30%) — *Over-Budget (+8.4%)*
   * **Savings:** 13.4% (Target: ≥ 20%) — *Deficit (-6.6%)*

---

## 💻 Advanced SQL Showcase (`sql/analysis_queries.sql`)

The repository includes enterprise-grade SQL queries demonstrating:
- **Common Table Expressions (CTEs)** for multi-stage financial rollups.
- **Window Functions (`LAG() OVER`)** for Month-over-Month (MoM) spend velocity.
- **Cumulative Window Sums (`SUM() OVER`)** for Pareto 80/20 vendor distribution.
- **Rolling Frame Windows (`ROWS BETWEEN 6 PRECEDING AND CURRENT ROW`)** for 7-day smoothed spending trajectories.
- **Budget vs. Actual Variance** cross-joins with conditional formatting logic.

---

## 🚀 Quick Start Guide

### 1. Clone & Set Up Environment
```bash
git clone https://github.com/your-username/finomaly.git
cd finomaly

# Install dependencies
pip install -r requirements.txt
```

### 2. Generate Data & Execute ETL Pipeline
```bash
# Generate synthetic raw transaction feeds
python src/generate_data.py

# Run ETL pipeline (cleans data & populates SQLite database)
python src/etl_pipeline.py
```

### 3. Launch Interactive Streamlit Dashboard
```bash
streamlit run app/app.py
```
*The dashboard will automatically open in your browser at `http://localhost:8501`.*

### 4. Explore the Jupyter Notebook
```bash
jupyter lab notebooks/SpendSense_EDA_and_Insights.ipynb
```

---

## 🛠️ Tech Stack & Methodologies
- **Language:** Python 3.11+
- **Data Wrangling:** Pandas, NumPy
- **Database & SQL:** SQLite3 (Schema DDL, Views, Window Functions, CTEs)
- **Data Visualization:** Plotly Express, Plotly Graph Objects, Seaborn, Matplotlib
- **Web App / BI:** Streamlit
- **Statistical Modeling:** Interquartile Range (IQR) Anomaly Detection, Holt’s Linear Trend Forecasting

---

## 📄 License
This project is licensed under the MIT License - feel free to use it for portfolio and educational purposes.
