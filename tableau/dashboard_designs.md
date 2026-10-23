# Finomaly — Tableau Dashboard Design Blueprints

This guide provides architectural specifications, visual hierarchy, layout containers, and interaction designs for four executive Tableau dashboards that connect directly to Finomaly exported data.

---

## Dashboard 1: Personal Finance Overview

### Purpose
High-level executive cockpit summarizing cash flow health, net savings rate velocity, and 50/30/20 budget compliance.

### Primary Dataset
- `monthly_financial_summaries_tableau.csv`

### Layout Structure (Desktop: 1440 × 900 px)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│  FINOMALY | Personal Finance Overview Dashboard                             │
│  Filters: [Fiscal Year] [Account Type] [Bucket: All]                        │
├───────────────────┬───────────────────┬───────────────────┬─────────────────┤
│ TOTAL INCOME      │ TOTAL EXPENSES    │ NET CASH FLOW     │ SAVINGS RATE    │
│ $112,400.00       │ $68,920.00        │ +$43,480.00       │ 38.7%           │
│ ▲ +8.2% vs prior  │ ▼ -3.1% vs prior  │ ▲ +14.5% velocity │ Target: ≥ 20.0% │
├───────────────────┴───────────────────┴───────────────────┴─────────────────┤
│ CASH FLOW TRAJECTORY (Dual-Axis Monthly Bar & Line)                         │
│ • Bars: Monthly Income (Teal #0D9488) and Monthly Expense (Slate #64748B)   │
│ • Line: Net Monthly Savings Rate % (Amber #F59E0B, Secondary Axis)          │
├───────────────────────────────────────┬─────────────────────────────────────┤
│ 50/30/20 BUDGET RULE AUDIT            │ CUMULATIVE RUNWAY & LIQUIDITY       │
│ 100% Stacked Bar by Month:            │ Area Chart of Rolling Savings       │
│ • Needs: 48.2% (Target ≤ 50%) [Cyan]  │ • Current Savings: $18,500.00       │
│ • Wants: 38.4% (Target ≤ 30%) [Rose]  │ • Monthly Burn Rate: $3,240.00      │
│ • Savings: 13.4% (Target ≥ 20%) [Emr] │ • Emergency Runway: 5.7 Months      │
└───────────────────────────────────────┴─────────────────────────────────────┘
```

---

## Dashboard 2: Expense Trends & Category Analysis

### Purpose
Granular breakdown of spending categories, merchant concentration (Pareto 80/20 rule), and temporal spending anomalies (Weekend vs Weekday surge).

### Primary Datasets
- `category_expenses_tableau.csv`
- `transactions_tableau.csv`

### Visualizations & Tableau Cards
1. **Category Share of Wallet (Donut Chart & Treemap):**
   - **Dimension:** `category`
   - **Measure:** `total_spend`
   - **Tooltip:** Includes `transaction_count`, `avg_ticket_size`, and `% of total spend`.
2. **Pareto 80/20 Merchant Concentration:**
   - **Dimension:** `clean_merchant` (Sorted descending by `total_spend`)
   - **Measure:** Bar chart of `total_spend` + Cumulative Window Sum Line (`RUNNING_SUM(SUM([amount])) / TOTAL(SUM([amount]))`).
   - Reference line at 80% to identify the vital few vendors driving the majority of discretionary spend.
3. **Temporal Heatmap (Day of Week vs Time of Month):**
   - **Rows:** `day_name` (Monday through Sunday)
   - **Columns:** `is_weekend`, `month`
   - **Color:** Average ticket size (revealing the +82% weekend spending surge).

---

## Dashboard 3: Budget Performance & Utilization

### Purpose
Real-time tracking of category-wise spending against targets, remaining balances, and alert thresholds.

### Primary Dataset
- `budget_vs_actual_tableau.csv`

### Visualizations & Tableau Cards
1. **Bullet Graphs for Category Budgets:**
   - **Primary Bar:** `actual_spent` (Dark Slate / Crimson if over budget)
   - **Reference Line:** `monthly_target`
   - **Shaded Ranges:** 60% (Safe), 80% (Approaching warning), 100% (Budget limit).
2. **Budget Status Scorecard:**
   - Visual KPIs counting categories in `HEALTHY`, `APPROACHING`, and `EXCEEDED` status.
3. **Variance Waterfall:**
   - Visualizing net surplus / deficit across each spending category.

---

## Dashboard 4: Spending Anomalies & Forecasts

### Purpose
Inspect machine learning Isolation Forest and IQR detected outliers, read plain-language justifications, and project future expenses with 95% confidence intervals.

### Primary Datasets
- `spending_anomalies_tableau.csv`
- `forecast_vs_actual_tableau.csv`

### Visualizations & Tableau Cards
1. **Historical vs Forward Expense Cone (Fan Chart):**
   - **X-Axis:** `period`
   - **Historical Line:** `actual_spend` (Solid Deep Teal)
   - **Forward Line:** `forecast_spend` (Dashed Cyan)
   - **Confidence Band:** Shaded polygon between `lower_bound_95` and `upper_bound_95` (representing 95% forecast cone).
2. **Anomaly Scatter Matrix:**
   - **X-Axis:** `date`
   - **Y-Axis:** `amount`
   - **Shape/Color:** `severity` (High: Crimson Circle, Medium: Amber Triangle, Low: Slate Square).
   - **Hover Action:** Displays `clean_merchant`, `comparison_metric`, `difference_amount`, and `explanation`.
3. **Anomaly Status Filter:**
   - Interactive dropdown to filter by `active`, `reviewed`, and `dismissed` alerts.
