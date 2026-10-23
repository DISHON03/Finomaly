# 💳 Finomaly: Intelligent Expense Analytics & Anomaly Detection Report

**Prepared For:** Senior Financial Stakeholders & Portfolio Reviewers  
**Role:** Lead Financial Data Analyst  
**Period Analyzed:** January 2024 – September 2026 (33 Months)  
**Dataset Scope:** 3,713 Validated Multi-Account Transactions  

---

## 1. Executive Summary & Problem Context
Personal cash flow management is often compromised by **spending opacity**: discretionary spending leakage, cumulative subscription creep, and seasonal expenditure spikes.

**Finomaly** was developed as an end-to-end data analytics and business intelligence engine to ingest raw, noisy multi-channel banking records, clean and normalize transaction records, store them in a relational SQLite data warehouse, and generate actionable financial insights using statistical analysis and predictive forecasting.

```
       RAW INGESTION                ETL & PIPELINE             ANALYTICS & BI
┌─────────────────────────┐    ┌─────────────────────────┐    ┌─────────────────────────┐
│ • Checking Feed (ACH)   │───▶│ • Regex Merchant Clean  │───▶│ • Streamlit Web App     │
│ • Credit Cards (Amex/CC)│    │ • Categorical Enrichment│    │ • 50/30/20 Compliance   │
│ • HYSA Savings Accounts │    │ • SQLite DB Warehouse   │    │ • Holt's Trend Forecast │
└─────────────────────────┘    └─────────────────────────┘    └─────────────────────────┘
```

---

## 2. Macro Financial Performance KPIs

| KPI Metric | Value | Benchmark / Target | Variance Status |
| :--- | :--- | :--- | :--- |
| **Total Inflow (Income)** | **$364,852.21** | — | Primary Earned Income |
| **Total Outflow (Expenditures)** | **$428,960.37** | — | Includes Fixed & Variable Spend |
| **Average Monthly Burn Rate** | **$12,998.80 / mo** | Baseline Target: $10,500 | Over Ideal Baseline |
| **Needs Allocation %** | **48.2%** | Target: ≤ 50.0% | ✅ Healthy Compliance |
| **Wants (Discretionary) %** | **38.4%** | Target: ≤ 30.0% | ⚠️ Over Discretionary Cap (+8.4%) |
| **Savings Allocation %** | **13.4%** | Target: ≥ 20.0% | ⚠️ Under Savings Goal (-6.6%) |
| **Active Subscriptions** | **9 Recurring Services** | Target: ≤ 5 Services | ⚠️ Subscription Leakage Identified |
| **Annualized Subscription Cost**| **$3,420.24 / year** | Target: < $1,800 / year | High Recurring Burden |

---

## 3. Key Findings & Empirical Discoveries

### A. The Pareto Principle (80/20 Merchant Rule)
* **The Vital Few:** Analysis indicates that **top 18 merchants account for 81.3% of cumulative expenditure**.
* **Housing Dominance:** Avalon Bay Apartments and ConEdison represent over 52% of total fixed living expenses.
* **E-Commerce & Food Velocity:** Amazon, Whole Foods, and DoorDash make up the bulk of non-fixed outlays, with transactions occurring 4.2 times per week on average.

### B. Weekend & Discretionary Surge Effect
* **Average Ticket Premium:** Transactions executed on Friday, Saturday, and Sunday exhibit an **average ticket size of $84.20**, compared to **$46.10 on weekdays** (+82.6% increase).
* **Delivery & Dining Concentration:** Over 68% of food delivery (DoorDash, UberEats) and dining spend occurs after 6:00 PM on Friday through Sunday.

### C. Subscription Creep & "Zombie" Recurring Outlays
* Over the 33-month observation window, 9 discrete recurring subscriptions were detected.
* While individual price points appear modest ($10.99–$185.00/mo), the aggregated commitment reaches **$3,420.24 annually**.
* **Redundancy:** Active simultaneous subscriptions to 4 distinct video streaming services (Netflix, HBO Max, YouTube Premium, Apple Services).

### D. Outlier & Capital Expense Shocks
* Using category-specific Interquartile Range (IQR) thresholding ($IQR \times 2.5$), 28 transactions were tagged as irregular capital outlays (e.g., Apple hardware purchases, emergency auto repairs, urgent dental procedures).
* These unbudgeted shocks caused negative monthly cash flow in 4 distinct quarters.

---

## 4. Predictive Forecasting & Cash Flow Projection
Using **Holt’s Linear Trend Exponential Smoothing** ($\alpha = 0.35, \beta = 0.15$):
* Projected next 6-month average monthly outflow: **$13,250 ± $820**.
* Seasonal surge expected in Q4 (November & December) due to holiday shopping and travel patterns (+22% over baseline).
* **Survival Runway:** At current average monthly burn, existing liquid savings ($25,000) provides **1.92 months of runway** under a zero-income shock.

---

## 5. Strategic Recommendations & Optimization Roadmap

| Priority | Strategy | Action Plan | Estimated Annual Wealth Impact |
| :---: | :--- | :--- | :---: |
| **P1** | **Discretionary Food Cap** | Cap weekly food delivery to 1 order; shift grocery shopping to Costco/Trader Joe's over Whole Foods. | **+$4,800 / year** |
| **P2** | **Subscription Consolidation** | Rotate streaming platforms; cancel inactive fitness or digital subscriptions; shift to annual billing. | **+$1,250 / year** |
| **P3** | **Automated 50/30/20 Protocol** | Implement bi-weekly split deposit: transfer 20% of net payroll straight into High-Yield Savings on payday. | **+$14,500 / year (Saved)** |
| **P4** | **Emergency Buffer Expansion** | Scale liquid emergency fund from 1.9 months to the recommended 6-month buffer ($78,000 target). | **Risk Mitigation** |

---

## 6. Project Artifacts
- **Interactive Dashboard:** `app/app.py` (Streamlit + Plotly)
- **Data Warehouse:** `data/processed/spendsense.db` (SQLite relational schema)
- **ETL Engine:** `src/etl_pipeline.py` (Data sanitization & feature engineering)
- **Analytical Notebook:** `notebooks/SpendSense_EDA_and_Insights.ipynb` (Full EDA, statistical models, visual plots)
- **Advanced SQL Suite:** `sql/analysis_queries.sql` (CTEs, Window Functions, Rolling Averages)
