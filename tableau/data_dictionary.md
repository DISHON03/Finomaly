# Finomaly — Tableau Reporting Layer Data Dictionary

This document details the schema, grain, data types, and business calculations for all six analytical reporting datasets exported by Finomaly for Tableau Desktop, Tableau Prep, and Tableau Public.

---

## 1. Transactions Feed (`transactions_tableau.csv`)
* **Grain:** One row per financial transaction.
* **Primary Key:** `transaction_id`

| Field Name | Data Type | Role | Description & Calculation Logic |
|---|---|---|---|
| `transaction_id` | String | Dimension | Unique transaction identifier (e.g. `TX_10001` or auto-generated `TX_42`). |
| `date` | Date (`YYYY-MM-DD`) | Dimension | Calendar posting date of the transaction. |
| `clean_merchant` | String | Dimension | Normalized, noise-reduced merchant name (e.g. "Trader Joe's", "Starbucks"). |
| `amount` | Decimal / Currency | Measure | Absolute transaction value in account currency. |
| `transaction_type` | String | Dimension | Cash flow direction: `Expense`, `Income`, or `Transfer`. |
| `category` | String | Dimension | Primary spending/income domain (e.g. `Housing`, `Food & Dining`, `Transportation`). |
| `subcategory` | String | Dimension | Detailed sub-classification (e.g. `Supermarkets`, `Coffee Shops`, `Rideshare`). |
| `budget_bucket` | String | Dimension | 50/30/20 category tier: `Needs`, `Wants`, `Savings`, or `Income`. |
| `is_recurring` | String | Dimension | `Yes` if verified subscription/bill cadence, otherwise `No`. |
| `payment_channel` | String | Dimension | Payment rail used: `Card`, `ACH Transfer`, `In-Store POS`, `Online`. |
| `city` | String | Dimension | Transaction terminal location or `Online`. |
| `state` | String | Dimension | Geographic state or region code (`NY`, `CA`, `US`). |
| `year` | Integer | Dimension | Extracted calendar year. |
| `month` | Integer | Dimension | Extracted calendar month (1-12). |
| `year_month` | String | Dimension | Standard fiscal period (`YYYY-MM`). |
| `day_name` | String | Dimension | Day of week (`Monday`, `Tuesday`, etc.). |
| `is_weekend` | String | Dimension | Temporal flag: `Weekend` (Saturday/Sunday) vs `Weekday` (Monday-Friday). |

---

## 2. Monthly Financial Summaries (`monthly_financial_summaries_tableau.csv`)
* **Grain:** One row per fiscal month (`year_month`).
* **Primary Key:** `year_month`

| Field Name | Data Type | Role | Description & Calculation Logic |
|---|---|---|---|
| `year_month` | String / Date | Dimension | Monthly aggregation period (`YYYY-MM`). |
| `total_income` | Decimal / Currency | Measure | Sum of all `Income` transactions within the month. |
| `total_expense` | Decimal / Currency | Measure | Sum of all `Expense` transactions within the month. |
| `net_cashflow` | Decimal / Currency | Measure | Net monthly savings: `total_income - total_expense`. |
| `savings_rate_pct` | Decimal / Percentage | Measure | Monthly savings velocity: `(net_cashflow / total_income) * 100`. |
| `needs_spend` | Decimal / Currency | Measure | Total expense allocated to essential living (`budget_bucket = 'Needs'`). |
| `wants_spend` | Decimal / Currency | Measure | Total expense allocated to discretionary lifestyle (`budget_bucket = 'Wants'`). |
| `needs_pct` | Decimal / Percentage | Measure | Needs compliance: `(needs_spend / total_income) * 100` (Benchmark: ≤ 50%). |
| `wants_pct` | Decimal / Percentage | Measure | Wants compliance: `(wants_spend / total_income) * 100` (Benchmark: ≤ 30%). |
| `savings_pct` | Decimal / Percentage | Measure | Savings compliance: `(net_cashflow / total_income) * 100` (Benchmark: ≥ 20%). |

---

## 3. Category-Wise Expenses (`category_expenses_tableau.csv`)
* **Grain:** One row per category and budget bucket.
* **Primary Key:** Composite (`category`, `budget_bucket`)

| Field Name | Data Type | Role | Description & Calculation Logic |
|---|---|---|---|
| `category` | String | Dimension | Primary expenditure category. |
| `budget_bucket` | String | Dimension | 50/30/20 classification: `Needs`, `Wants`, or `Savings`. |
| `total_spend` | Decimal / Currency | Measure | Cumulative historical expenditure in this category. |
| `transaction_count` | Integer | Measure | Total count of recorded expense transactions. |
| `avg_ticket_size` | Decimal / Currency | Measure | Average spend per transaction: `total_spend / transaction_count`. |
| `pct_of_total_spend` | Decimal / Percentage | Measure | Share of wallet: `(total_spend / grand_total_expenses) * 100`. |

---

## 4. Budget vs Actual Performance (`budget_vs_actual_tableau.csv`)
* **Grain:** One row per budgeted category for the active reporting period.
* **Primary Key:** Composite (`year_month`, `category`)

| Field Name | Data Type | Role | Description & Calculation Logic |
|---|---|---|---|
| `year_month` | String | Dimension | Fiscal period being monitored. |
| `category` | String | Dimension | Budgeted spending category. |
| `budget_bucket` | String | Dimension | `Needs` or `Wants`. |
| `monthly_target` | Decimal / Currency | Measure | Monthly spending allocation target set by the user. |
| `actual_spent` | Decimal / Currency | Measure | Real-time recorded expense in current period. |
| `remaining_budget` | Decimal / Currency | Measure | Residual budget capacity: `monthly_target - actual_spent`. |
| `utilization_pct` | Decimal / Percentage | Measure | Budget burn percentage: `(actual_spent / monthly_target) * 100`. |
| `performance_status`| String | Dimension | `HEALTHY` (< threshold), `APPROACHING` (≥ threshold), or `EXCEEDED` (> 100%). |

---

## 5. Spending Anomalies & Outliers (`spending_anomalies_tableau.csv`)
* **Grain:** One row per flagged spending outlier or category surge.
* **Primary Key:** `alert_id`

| Field Name | Data Type | Role | Description & Calculation Logic |
|---|---|---|---|
| `alert_id` | Integer | Dimension | Unique anomaly alert identifier. |
| `date` | Date | Dimension | Date transaction occurred or anomaly was detected. |
| `clean_merchant` | String | Dimension | Flagged merchant name or category aggregate. |
| `amount` | Decimal / Currency | Measure | Transaction amount flagged as anomalous. |
| `category` | String | Dimension | Associated spending category. |
| `alert_type` | String | Dimension | `AMOUNT_SPIKE`, `CATEGORY_SURGE`, or `UNUSUAL_CADENCE`. |
| `severity` | String | Dimension | Outlier impact rating: `LOW`, `MEDIUM`, or `HIGH`. |
| `comparison_metric` | String | Dimension | Baseline comparison (e.g. "3.5x category median ($42.00)"). |
| `difference_amount` | Decimal / Currency | Measure | Numerical dollar variance above baseline threshold. |
| `status` | String | Dimension | Alert lifecycle state: `active`, `reviewed`, or `dismissed`. |
| `explanation` | String | Dimension | Descriptive explanation of statistical deviation without false fraud claims. |

---

## 6. Forecast vs Actual Expenses (`forecast_vs_actual_tableau.csv`)
* **Grain:** One row per fiscal month (trailing historical + forward forecast).
* **Primary Key:** `period`

| Field Name | Data Type | Role | Description & Calculation Logic |
|---|---|---|---|
| `period` | String / Date | Dimension | Month identifier (`YYYY-MM`). |
| `actual_spend` | Decimal / Currency | Measure | Real historical monthly expense (null for future months). |
| `forecast_spend` | Decimal / Currency | Measure | Projected spend based on Double Exponential Smoothing (Holt's Linear Trend). |
| `lower_bound_95` | Decimal / Currency | Measure | 95% confidence interval lower limit: `forecast - 1.96 * sigma * sqrt(h)`. |
| `upper_bound_95` | Decimal / Currency | Measure | 95% confidence interval upper limit: `forecast + 1.96 * sigma * sqrt(h)`. |
| `is_forecast` | String | Dimension | Label distinguishing `Actual` historical data from `Forecast` projections. |
| `model_used` | String | Dimension | Predictive method (e.g. "Holt's Linear Trend (Double Exponential Smoothing)"). |
