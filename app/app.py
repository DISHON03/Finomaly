"""
Finomaly - Interactive Financial Analytics & Anomaly Detection Dashboard
Built with Streamlit & Plotly
"""

import os
import sqlite3
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Configure page layout
st.set_page_config(
    page_title="Finomaly | Intelligent Expense Analytics & Anomaly Detection",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Base Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "clean_transactions.csv")
DB_PATH = os.path.join(BASE_DIR, "data", "processed", "spendsense.db")

@st.cache_data
def load_data():
    if not os.path.exists(DATA_PATH):
        st.error(f"Data file not found at {DATA_PATH}. Please run `python src/etl_pipeline.py` first.")
        st.stop()
    df = pd.read_csv(DATA_PATH)
    df["date"] = pd.to_datetime(df["date"])
    return df

@st.cache_data
def load_budgets():
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    conn = sqlite3.connect(DB_PATH)
    budgets_df = pd.read_sql_query("SELECT * FROM budgets;", conn)
    conn.close()
    return budgets_df

# Load datasets
raw_df = load_data()
budgets_df = load_budgets()

# -------------------------------------------------------------
# SIDEBAR FILTERS
# -------------------------------------------------------------
st.sidebar.image("https://img.icons8.com/isometric/100/money-box.png", width=70)
st.sidebar.title("Finomaly Analytics")
st.sidebar.markdown("**Intelligent Expense Analytics & Anomaly Detection**")
st.sidebar.markdown("---")

# Date range filter
min_date = raw_df["date"].min().date()
max_date = raw_df["date"].max().date()

date_selection = st.sidebar.date_input(
    "Date Range",
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

if isinstance(date_selection, (list, tuple)) and len(date_selection) == 2:
    start_d, end_d = date_selection
else:
    start_d, end_d = min_date, max_date

# Account filter
all_accounts = sorted(raw_df["account_id"].unique())
account_mapping = {
    "ACC_CHK_01": "Chase Checking",
    "ACC_SAV_01": "Ally Savings",
    "ACC_CC_01": "Chase Sapphire Preferred",
    "ACC_CC_02": "Amex Blue Cash"
}
account_options = [f"{acc} - {account_mapping.get(acc, acc)}" for acc in all_accounts]
selected_acc_labels = st.sidebar.multiselect("Select Accounts", options=account_options, default=account_options)
selected_accs = [s.split(" - ")[0] for s in selected_acc_labels]

# Category filter
all_categories = sorted(raw_df[raw_df["transaction_type"] == "Expense"]["category"].unique())
selected_categories = st.sidebar.multiselect("Expense Categories", options=all_categories, default=all_categories)

# Apply filters
df = raw_df[
    (raw_df["date"].dt.date >= start_d) &
    (raw_df["date"].dt.date <= end_d) &
    (raw_df["account_id"].isin(selected_accs))
].copy()

# Include Income & Transfers even if category filter is active (category filter applies to expenses)
df = df[
    (df["transaction_type"].isin(["Income", "Transfer"])) |
    (df["category"].isin(selected_categories))
]

st.sidebar.markdown("---")
st.sidebar.info(
    f"Filtered Dataset: **{len(df):,}** transactions across **{df['year_month'].nunique()}** months."
)

# -------------------------------------------------------------
# TOP HEADER & OVERVIEW
# -------------------------------------------------------------
st.title("💳 Finomaly | Intelligent Expense Analytics & Anomaly Detection")
st.markdown("Understand Your Spending. Detect the Unusual. An end-to-end analytical view of cash flow, category velocity, 50/30/20 budget adherence, and subscription leakage.")

# Calculate global KPIs
expense_df = df[df["transaction_type"] == "Expense"]
income_df = df[df["transaction_type"] == "Income"]
transfer_df = df[df["transaction_type"] == "Transfer"]

total_spend = expense_df["amount"].sum()
total_income = income_df["amount"].sum()
net_cashflow = total_income - total_spend
savings_rate = (net_cashflow / total_income * 100) if total_income > 0 else 0.0
months_active = max(df["year_month"].nunique(), 1)
burn_rate = total_spend / months_active

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpi1.metric("💰 Total Inflow", f"${total_income:,.2f}")
kpi2.metric("💸 Total Outflow", f"${total_spend:,.2f}", delta=f"-${burn_rate:,.0f}/mo avg", delta_color="inverse")
kpi3.metric("📈 Net Savings", f"${net_cashflow:,.2f}", delta=f"{savings_rate:.1f}% rate")
kpi4.metric("🔥 Monthly Burn Rate", f"${burn_rate:,.2f}")
kpi5.metric("📦 Active Tx Count", f"{len(df):,}")

st.markdown("---")

# -------------------------------------------------------------
# MAIN DASHBOARD TABS
# -------------------------------------------------------------
tabs = st.tabs([
    "📊 Cash Flow & Trends",
    "🔍 Category & Pareto Analysis",
    "⚖️ 50/30/20 Budget Audit",
    "🕵️ Subscriptions & Anomalies",
    "📈 Forecast & Runway Simulator",
    "🗃️ Transaction Explorer"
])

# =============================================================
# TAB 1: Cash Flow & Trends
# =============================================================
with tabs[0]:
    st.subheader("Monthly Cash Flow & Savings Trajectory")
    
    monthly_cf = df.groupby(["year_month", "transaction_type"])["amount"].sum().unstack(fill_value=0).reset_index()
    for col in ["Expense", "Income", "Transfer"]:
        if col not in monthly_cf.columns:
            monthly_cf[col] = 0.0

    monthly_cf["Net_Savings"] = monthly_cf["Income"] - monthly_cf["Expense"]
    monthly_cf["Cumulative_Savings"] = monthly_cf["Net_Savings"].cumsum()
    monthly_cf["Savings_Rate_Pct"] = np.where(monthly_cf["Income"] > 0, (monthly_cf["Net_Savings"] / monthly_cf["Income"] * 100).round(1), 0.0)

    # Plot 1: Income vs Expense bar chart with Net Savings line
    fig_cf = go.Figure()
    fig_cf.add_trace(go.Bar(
        x=monthly_cf["year_month"],
        y=monthly_cf["Income"],
        name="Income",
        marker_color="#2ecc71"
    ))
    fig_cf.add_trace(go.Bar(
        x=monthly_cf["year_month"],
        y=monthly_cf["Expense"],
        name="Expense",
        marker_color="#e74c3c"
    ))
    fig_cf.add_trace(go.Scatter(
        x=monthly_cf["year_month"],
        y=monthly_cf["Net_Savings"],
        name="Net Cashflow",
        mode="lines+markers",
        line=dict(color="#3498db", width=3)
    ))
    fig_cf.update_layout(
        title="Monthly Income vs. Outflow with Net Savings",
        barmode="group",
        xaxis_title="Month",
        yaxis_title="Amount ($)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_white",
        height=420
    )
    st.plotly_chart(fig_cf, use_container_width=True)

    col_t1a, col_t1b = st.columns(2)
    with col_t1a:
        # Plot 2: Cumulative Wealth Trajectory
        fig_cum = px.area(
            monthly_cf,
            x="year_month",
            y="Cumulative_Savings",
            title="Cumulative Net Wealth Accumulated Over Time",
            color_discrete_sequence=["#1abc9c"]
        )
        fig_cum.update_layout(template="plotly_white", xaxis_title="Month", yaxis_title="Cumulative Net ($)", height=350)
        st.plotly_chart(fig_cum, use_container_width=True)

    with col_t1b:
        # Plot 3: Savings Rate Percentage
        fig_sr = px.line(
            monthly_cf,
            x="year_month",
            y="Savings_Rate_Pct",
            title="Monthly Savings Rate % (Benchmark: ≥ 20%)",
            markers=True,
            color_discrete_sequence=["#9b59b6"]
        )
        fig_sr.add_hline(y=20, line_dash="dash", line_color="green", annotation_text="Target 20% Goal")
        fig_sr.update_layout(template="plotly_white", xaxis_title="Month", yaxis_title="Savings Rate (%)", height=350)
        st.plotly_chart(fig_sr, use_container_width=True)

# =============================================================
# TAB 2: Category & Pareto Analysis
# =============================================================
with tabs[1]:
    st.subheader("Spending Distribution, Hierarchy & Pareto 80/20 Analysis")

    col_cat1, col_cat2 = st.columns([1.1, 0.9])

    with col_cat1:
        # Sunburst Chart for Category Hierarchy
        sunburst_df = expense_df.groupby(["category", "subcategory"])["amount"].sum().reset_index()
        fig_sun = px.sunburst(
            sunburst_df,
            path=["category", "subcategory"],
            values="amount",
            title="Interactive Spending Sunburst (Category → Subcategory)",
            color="amount",
            color_continuous_scale="Blues"
        )
        fig_sun.update_layout(height=480)
        st.plotly_chart(fig_sun, use_container_width=True)

    with col_cat2:
        # Category Spend Donut
        cat_totals = expense_df.groupby("category")["amount"].sum().reset_index().sort_values(by="amount", ascending=False)
        fig_pie = px.pie(
            cat_totals,
            names="category",
            values="amount",
            hole=0.45,
            title="Spending Share by Major Category",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_pie.update_layout(height=480)
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")
    st.subheader("Pareto 80/20 Merchant Concentration")
    st.markdown("According to the Pareto Principle, approximately 80% of personal expenses are concentrated in roughly 20% of merchants. Identifying these vendors highlights the highest-leverage targets for financial optimization.")

    # Pareto calculation
    merchant_agg = expense_df.groupby("clean_merchant")["amount"].agg(total_spend="sum", count="count").reset_index()
    merchant_agg = merchant_agg.sort_values(by="total_spend", ascending=False).reset_index(drop=True)
    merchant_agg["cum_spend"] = merchant_agg["total_spend"].cumsum()
    grand_exp = merchant_agg["total_spend"].sum()
    merchant_agg["cum_pct"] = (merchant_agg["cum_spend"] / grand_exp * 100).round(2)
    merchant_agg["rank"] = merchant_agg.index + 1
    merchant_agg["merchant_pct"] = (merchant_agg["rank"] / len(merchant_agg) * 100).round(2)

    top20_merchants = merchant_agg.head(20)

    fig_pareto = go.Figure()
    fig_pareto.add_trace(go.Bar(
        x=top20_merchants["clean_merchant"],
        y=top20_merchants["total_spend"],
        name="Merchant Total Spend ($)",
        marker_color="#34495e"
    ))
    fig_pareto.add_trace(go.Scatter(
        x=top20_merchants["clean_merchant"],
        y=top20_merchants["cum_pct"],
        name="Cumulative Spend %",
        mode="lines+markers",
        yaxis="y2",
        line=dict(color="#e67e22", width=3)
    ))
    fig_pareto.update_layout(
        title="Top 20 Outlay Merchants vs. Cumulative Spend Curve",
        xaxis_title="Merchant Name",
        yaxis=dict(title="Spend Amount ($)"),
        yaxis2=dict(title="Cumulative %", overlaying="y", side="right", range=[0, 105]),
        template="plotly_white",
        height=450,
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig_pareto, use_container_width=True)

    # Weekend vs Weekday analysis
    st.markdown("---")
    st.subheader("Day-of-Week Behavioral Analysis")
    dow_df = expense_df.groupby(["day_name", "is_weekend"])["amount"].agg(total="sum", avg_ticket="mean", count="count").reset_index()
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dow_df["day_name"] = pd.Categorical(dow_df["day_name"], categories=day_order, ordered=True)
    dow_df = dow_df.sort_values(by="day_name")

    col_dow1, col_dow2 = st.columns(2)
    with col_dow1:
        fig_dow = px.bar(
            dow_df,
            x="day_name",
            y="total",
            color="is_weekend",
            labels={"is_weekend": "Is Weekend"},
            title="Total Spend Volume by Day of Week",
            color_discrete_map={0: "#3498db", 1: "#e74c3c"}
        )
        fig_dow.update_layout(template="plotly_white", xaxis_title="Day", yaxis_title="Total ($)", height=350)
        st.plotly_chart(fig_dow, use_container_width=True)

    with col_dow2:
        fig_ticket = px.line(
            dow_df,
            x="day_name",
            y="avg_ticket",
            markers=True,
            title="Average Ticket Size ($) Across Weekdays vs. Weekends",
            color_discrete_sequence=["#27ae60"]
        )
        fig_ticket.update_layout(template="plotly_white", xaxis_title="Day", yaxis_title="Average Ticket ($)", height=350)
        st.plotly_chart(fig_ticket, use_container_width=True)

# =============================================================
# TAB 3: 50/30/20 Budget Audit
# =============================================================
with tabs[2]:
    st.subheader("50 / 30 / 20 Budget Rule Compliance Audit")
    st.markdown(
        """
        The **50/30/20 Rule** provides a foundational financial health benchmark:
        - **50% Needs**: Housing, utilities, groceries, transport, essential healthcare.
        - **30% Wants**: Dining out, entertainment, shopping, vacations.
        - **20% Savings**: Emergency fund, investments, debt principal repayment.
        """
    )

    # Calculate actual percentage totals across filtered slice
    needs_tot = df[(df["budget_bucket"] == "Needs") & (df["transaction_type"] == "Expense")]["amount"].sum()
    wants_tot = df[(df["budget_bucket"] == "Wants") & (df["transaction_type"] == "Expense")]["amount"].sum()
    savings_tot = df[(df["budget_bucket"] == "Savings") | (df["transaction_type"] == "Transfer")]["amount"].sum()
    inc_tot = total_income if total_income > 0 else 1.0

    pct_needs = round((needs_tot / inc_tot) * 100, 1)
    pct_wants = round((wants_tot / inc_tot) * 100, 1)
    pct_savings = round((savings_tot / inc_tot) * 100, 1)

    c_b1, c_b2, c_b3 = st.columns(3)
    c_b1.metric("🏠 Needs Allocation", f"{pct_needs}%", delta="Target: ≤ 50%", delta_color="inverse" if pct_needs > 50 else "normal")
    c_b2.metric("🎉 Wants (Discretionary)", f"{pct_wants}%", delta="Target: ≤ 30%", delta_color="inverse" if pct_wants > 30 else "normal")
    c_b3.metric("🌱 Savings & Investments", f"{pct_savings}%", delta="Target: ≥ 20%", delta_color="normal" if pct_savings >= 20 else "inverse")

    # Time-series stacked area chart of the 3 buckets
    monthly_buckets = df.pivot_table(
        index="year_month",
        columns="budget_bucket",
        values="amount",
        aggfunc="sum",
        fill_value=0
    ).reset_index()

    for col in ["Needs", "Wants", "Savings"]:
        if col not in monthly_buckets.columns:
            monthly_buckets[col] = 0.0

    fig_bucket_trend = px.bar(
        monthly_buckets,
        x="year_month",
        y=["Needs", "Wants", "Savings"],
        title="Monthly Spend by Budget Bucket",
        color_discrete_map={"Needs": "#3498db", "Wants": "#e67e22", "Savings": "#2ecc71"},
        barmode="stack"
    )
    fig_bucket_trend.update_layout(template="plotly_white", xaxis_title="Month", yaxis_title="Amount ($)", height=400)
    st.plotly_chart(fig_bucket_trend, use_container_width=True)

    # Budget vs Actual Variance Table
    st.subheader("Category Budget vs. Actual Monthly Variance")
    if not budgets_df.empty:
        actual_cat_monthly = expense_df.groupby("category")["amount"].sum() / months_active
        variance_df = budgets_df.copy()
        variance_df["actual_monthly_spend"] = variance_df["category"].map(actual_cat_monthly).fillna(0).round(2)
        variance_df["variance_dollar"] = (variance_df["actual_monthly_spend"] - variance_df["monthly_budget_target"]).round(2)
        variance_df["variance_pct"] = ((variance_df["variance_dollar"] / variance_df["monthly_budget_target"]) * 100).round(1)
        variance_df["status"] = variance_df["variance_dollar"].apply(lambda v: "⚠️ Over Budget" if v > 0 else "✅ Within Budget")

        st.dataframe(
            variance_df.style.map(
                lambda v: "color: red; font-weight: bold" if "Over Budget" in str(v) else "color: green",
                subset=["status"]
            ),
            use_container_width=True
        )

# =============================================================
# TAB 4: Subscriptions & Anomalies
# =============================================================
with tabs[3]:
    st.subheader("Recurring Subscription Audit & Leakage Detection")
    st.markdown("Subscriptions often cause silent financial leakage. Here is an audit of detected recurring services and their 12-month projected impact.")

    sub_df = df[(df["is_recurring"] == 1) & (df["transaction_type"] == "Expense")]
    if not sub_df.empty:
        sub_audit = sub_df.groupby(["clean_merchant", "category", "subcategory"]).agg(
            avg_monthly_cost=("amount", "mean"),
            active_months=("year_month", "nunique"),
            total_paid=("amount", "sum")
        ).reset_index()
        sub_audit["avg_monthly_cost"] = sub_audit["avg_monthly_cost"].round(2)
        sub_audit["total_paid"] = sub_audit["total_paid"].round(2)
        sub_audit["annual_projected_cost"] = (sub_audit["avg_monthly_cost"] * 12).round(2)
        sub_audit = sub_audit.sort_values(by="annual_projected_cost", ascending=False)

        total_annual_sub = sub_audit["annual_projected_cost"].sum()
        sub_kpi1, sub_kpi2 = st.columns(2)
        sub_kpi1.metric("🔔 Active Recurring Services", f"{len(sub_audit)} Subscriptions")
        sub_kpi2.metric("💳 Annualized Subscription Burn", f"${total_annual_sub:,.2f}/yr", delta=f"${total_annual_sub/12:,.2f}/mo")

        fig_sub = px.bar(
            sub_audit,
            x="clean_merchant",
            y="annual_projected_cost",
            color="category",
            text_auto=".2s",
            title="Projected 12-Month Annual Cost per Subscription Service",
            color_discrete_sequence=px.colors.qualitative.Dark24
        )
        fig_sub.update_layout(template="plotly_white", xaxis_title="Subscription / Merchant", yaxis_title="Annual Run-rate ($)", height=380)
        st.plotly_chart(fig_sub, use_container_width=True)

        st.dataframe(sub_audit, use_container_width=True)

    st.markdown("---")
    st.subheader("Statistical Anomaly & Outlier Detection (Category IQR)")
    st.markdown("Flagging high-magnitude or atypical transactions exceeding 2.5x the Interquartile Range (IQR) for their category.")

    # Calculate IQR outliers
    outliers = []
    for cat, grp in expense_df.groupby("category"):
        q25 = grp["amount"].quantile(0.25)
        q75 = grp["amount"].quantile(0.75)
        iqr = q75 - q25
        upper_limit = max(q75 + (2.5 * iqr), 120.0)
        flagged = grp[grp["amount"] > upper_limit].copy()
        if not flagged.empty:
            flagged["category_upper_limit"] = round(upper_limit, 2)
            flagged["anomaly_delta"] = (flagged["amount"] - upper_limit).round(2)
            outliers.append(flagged)

    if outliers:
        outlier_table = pd.concat(outliers).sort_values(by="amount", ascending=False)
        st.warning(f"Detected {len(outlier_table)} statistically anomalous transactions.")
        st.dataframe(
            outlier_table[[
                "date", "clean_merchant", "category", "subcategory", "amount",
                "category_upper_limit", "anomaly_delta", "account_id"
            ]],
            use_container_width=True
        )
    else:
        st.success("No critical outliers detected within current filters.")

# =============================================================
# TAB 5: Forecast & Runway Simulator
# =============================================================
with tabs[4]:
    st.subheader("Holt's Linear Trend Expense Forecast (6 Months)")
    
    monthly_series = expense_df.groupby("year_month")["amount"].sum().reset_index()
    monthly_series["date_parsed"] = pd.to_datetime(monthly_series["year_month"] + "-01")
    monthly_series = monthly_series.sort_values(by="date_parsed").reset_index(drop=True)

    if len(monthly_series) >= 6:
        # Holt's linear trend forecast
        y = monthly_series["amount"].values
        alpha, beta = 0.35, 0.15
        level, trend = y[0], y[1] - y[0]
        fitted = [level + trend]
        for t in range(1, len(y)):
            val = y[t]
            last_l, last_tr = level, trend
            level = alpha * val + (1 - alpha) * (last_l + last_tr)
            trend = beta * (level - last_l) + (1 - beta) * last_tr
            fitted.append(level + trend)

        residuals = y - np.array(fitted)
        sigma = np.std(residuals)

        last_dt = monthly_series["date_parsed"].iloc[-1]
        forecast_dates, f_vals, f_lower, f_upper = [], [], [], []
        for h in range(1, 7):
            f_dt = last_dt + pd.DateOffset(months=h)
            pred = level + h * trend
            margin = 1.96 * sigma * np.sqrt(h)
            forecast_dates.append(f_dt.strftime("%Y-%m"))
            f_vals.append(round(pred, 2))
            f_lower.append(max(0, round(pred - margin, 2)))
            f_upper.append(round(pred + margin, 2))

        fig_fc = go.Figure()
        # Historical actuals
        fig_fc.add_trace(go.Scatter(
            x=monthly_series["year_month"],
            y=monthly_series["amount"],
            name="Actual Outflow",
            mode="lines+markers",
            line=dict(color="#2980b9", width=2.5)
        ))
        # Forecast
        fig_fc.add_trace(go.Scatter(
            x=forecast_dates,
            y=f_vals,
            name="Forecasted Outflow",
            mode="lines+markers",
            line=dict(color="#e74c3c", width=2.5, dash="dash")
        ))
        # Upper bound
        fig_fc.add_trace(go.Scatter(
            x=forecast_dates,
            y=f_upper,
            name="95% Upper Bound",
            mode="lines",
            line=dict(width=0),
            showlegend=False
        ))
        # Lower bound
        fig_fc.add_trace(go.Scatter(
            x=forecast_dates,
            y=f_lower,
            name="95% Confidence Interval",
            mode="lines",
            fill="tonexty",
            fillcolor="rgba(231, 76, 60, 0.2)",
            line=dict(width=0)
        ))
        fig_fc.update_layout(
            title="Monthly Expense Forecast (Next 6 Months with 95% Confidence Bounds)",
            xaxis_title="Month",
            yaxis_title="Expense ($)",
            template="plotly_white",
            height=420
        )
        st.plotly_chart(fig_fc, use_container_width=True)

    st.markdown("---")
    st.subheader("Interactive 'What-If' Budget Scenario Simulator")
    st.markdown("Simulate how targeted spending cutbacks impact your net annual savings.")

    col_sim1, col_sim2, col_sim3 = st.columns(3)
    cut_dining = col_sim1.slider("Dining & Food Delivery Cutback (%)", 0, 50, 15)
    cut_subs = col_sim2.slider("Streaming & Subscriptions Cutback (%)", 0, 50, 20)
    cut_shopping = col_sim3.slider("Shopping & Retail Cutback (%)", 0, 50, 25)

    annual_dining = expense_df[expense_df["category"] == "Food & Dining"]["amount"].sum() / months_active * 12
    annual_subs = expense_df[expense_df["category"] == "Entertainment & Subscriptions"]["amount"].sum() / months_active * 12
    annual_shop = expense_df[expense_df["category"] == "Shopping & Retail"]["amount"].sum() / months_active * 12

    saved_dining = annual_dining * (cut_dining / 100)
    saved_subs = annual_subs * (cut_subs / 100)
    saved_shop = annual_shop * (cut_shopping / 100)
    total_annual_saved = saved_dining + saved_subs + saved_shop

    sim_res1, sim_res2, sim_res3 = st.columns(3)
    sim_res1.metric("💡 Food & Dining Annual Savings", f"${saved_dining:,.2f}")
    sim_res2.metric("💡 Entertainment Annual Savings", f"${saved_subs:,.2f}")
    sim_res3.metric("🎉 TOTAL ANNUAL WEALTH GAIN", f"+${total_annual_saved:,.2f}", delta="Instant annual savings")

    # Emergency runway calculator
    st.markdown("---")
    st.subheader("Emergency Reserve & Survival Runway")
    cur_savings = st.number_input("Enter Total Liquid Savings / Emergency Fund ($)", value=25000, step=1000)
    survival_months = round(cur_savings / burn_rate, 1) if burn_rate > 0 else 99.0
    rec_3mo = round(burn_rate * 3, 2)
    rec_6mo = round(burn_rate * 6, 2)

    st.info(
        f"At your current average monthly burn rate of **${burn_rate:,.2f}**, your savings provides **{survival_months} months** of runway with zero income. "
        f"Recommended 3-month safety target: **${rec_3mo:,.2f}** | 6-month safety target: **${rec_6mo:,.2f}**."
    )

# =============================================================
# TAB 6: Transaction Explorer
# =============================================================
with tabs[5]:
    st.subheader("Filterable Raw & Cleaned Transaction Ledger")
    
    # Keyword search
    search_term = st.text_input("🔍 Search by Merchant, Description or City", "")
    filtered_table = df.copy()
    if search_term:
        term = search_term.lower()
        filtered_table = filtered_table[
            filtered_table["clean_merchant"].str.lower().str.contains(term) |
            filtered_table["raw_description"].str.lower().str.contains(term) |
            filtered_table["city"].str.lower().str.contains(term)
        ]

    st.write(f"Displaying **{len(filtered_table):,}** matching transactions:")
    st.dataframe(
        filtered_table[[
            "date", "account_id", "clean_merchant", "amount", "transaction_type",
            "category", "subcategory", "budget_bucket", "payment_channel", "city"
        ]].sort_values(by="date", ascending=False),
        use_container_width=True,
        height=400
    )

    # Download CSV button
    csv_bytes = filtered_table.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Export Filtered Ledger as CSV",
        data=csv_bytes,
        file_name="finomaly_filtered_transactions.csv",
        mime="text/csv"
    )

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #7f8c8d;'>"
    "Finomaly Portfolio Project &bull; Built with Python, SQLite, Streamlit & Plotly &bull; Understand Your Spending. Detect the Unusual."
    "</div>",
    unsafe_allow_html=True
)
