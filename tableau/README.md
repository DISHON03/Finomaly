# 📊 Finomaly — Tableau Analytics Integration Guide

Finomaly provides a Tableau-compatible analytical reporting layer. It enables users to connect **Tableau Desktop**, **Tableau Prep**, or the free **Tableau Public** application to explore interactive personal finance dashboards.

---

## 📁 Exported Reporting Datasets

All six datasets are automatically kept up-to-date and stored in `tableau/exports/`. They can also be dynamically downloaded in real time from the Finomaly web application under the **Tableau Analytics** page or via the API:

1. **`transactions_tableau.csv`**: Granular transaction ledger with temporal, merchant, and calendar features.
2. **`monthly_financial_summaries_tableau.csv`**: Monthly cash flows, net savings rate, and 50/30/20 compliance.
3. **`category_expenses_tableau.csv`**: Category expenditure totals, transaction counts, ticket sizes, and share of wallet.
4. **`budget_vs_actual_tableau.csv`**: Category budget performance, utilization %, and warning indicators.
5. **`spending_anomalies_tableau.csv`**: ML Isolation Forest & IQR outlier alerts with severity and explanation metrics.
6. **`forecast_vs_actual_tableau.csv`**: Historical timeline combined with forward Holt's Linear Trend projections and 95% confidence bands.

---

## 🚀 How to Connect Tableau Desktop or Tableau Public

### Method A: Connect Directly to CSV Exports (Recommended & Free with Tableau Public)
1. Open **Tableau Desktop** or **Tableau Public** (Download free from [public.tableau.com](https://public.tableau.com)).
2. Under **Connect** on the left sidebar, select **Text file**.
3. Navigate to the Finomaly project folder:
   `c:\Users\HP\Downloads\Spendsense\tableau\exports\`
4. Select any dataset (e.g., `transactions_tableau.csv` or `monthly_financial_summaries_tableau.csv`).
5. Click **Open**. Tableau will display the data preview grid.
6. Click **Sheet 1** at the bottom to start building interactive visualizations!

### Method B: Connecting Multiple Tables & Relationships in Tableau
1. In the Tableau Data Source pane, drag `monthly_financial_summaries_tableau.csv` as the root table.
2. Drag `forecast_vs_actual_tableau.csv` onto the canvas and create a relationship on `year_month = period`.
3. Drag `budget_vs_actual_tableau.csv` to connect on `year_month = year_month`.

### Method C: Live SQLite Database Connection (Tableau Desktop / Prep)
If you have Tableau Desktop with SQLite ODBC driver:
1. Under **Connect -> To a Server**, select **Other Databases (ODBC)**.
2. Select SQLite3 ODBC Driver.
3. Database Name: `c:\Users\HP\Downloads\Spendsense\data\processed\spendsense_app.db`.
4. Connect directly to the SQLite tables and views (`transactions`, `budgets`, `anomaly_alerts`).

---

## 🎨 Recommended Visuals to Build

| Dashboard | Visual | Key Dimensions & Measures |
|---|---|---|
| **Overview** | Cash Flow Velocity | `year_month` (Cols), `SUM(total_income)` & `SUM(total_expense)` (Rows) |
| **Overview** | Savings Rate Dual-Axis | `savings_rate_pct` as Line on secondary axis |
| **Overview** | 50/30/20 Stacked Bar | `needs_pct`, `wants_pct`, `savings_pct` (100% Bar) |
| **Categories** | Treemap / Donut | `category` (Color), `total_spend` (Size/Label) |
| **Categories** | Pareto 80/20 Chart | `clean_merchant` (Sorted Desc), Running % Sum of `total_spend` |
| **Budgets** | Bullet Graph | `actual_spent` vs `monthly_target` reference line |
| **Anomalies** | Outlier Scatter | `date` (X), `amount` (Y), `severity` (Color: Red/Amber) |
| **Forecasting** | 95% Confidence Cone | `period` (X), Dual-axis `actual_spend` + `forecast_spend`, shaded area between `lower_bound_95` and `upper_bound_95` |

---

## 🔒 Security & Privacy Note
The Tableau exports contain **zero banking credentials, passwords, or account numbers**. All financial records exported are categorized analytics data or synthetic demo profiles.
