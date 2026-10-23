"""
Finomaly - Core Analytics Module
Calculates financial KPIs, budget compliance (50/30/20), category velocity,
Pareto 80/20 merchant distributions, subscription leakage, and anomaly detection.
"""

import pandas as pd
import numpy as np

def compute_kpis(df):
    """
    Computes overarching executive financial KPIs across the dataset or a filtered slice.
    """
    expense_mask = df["transaction_type"] == "Expense"
    income_mask = df["transaction_type"] == "Income"
    transfer_mask = df["transaction_type"] == "Transfer"

    total_spend = df.loc[expense_mask, "amount"].sum()
    total_income = df.loc[income_mask, "amount"].sum()
    total_transfers = df.loc[transfer_mask, "amount"].sum()
    
    net_savings = total_income - total_spend
    savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0.0

    # Needs vs Wants split
    needs_spend = df.loc[expense_mask & (df["budget_bucket"] == "Needs"), "amount"].sum()
    wants_spend = df.loc[expense_mask & (df["budget_bucket"] == "Wants"), "amount"].sum()
    discretionary_ratio = (wants_spend / total_spend * 100) if total_spend > 0 else 0.0

    # Average monthly burn rate
    months_count = max(df["year_month"].nunique(), 1)
    monthly_burn_rate = total_spend / months_count
    monthly_income_avg = total_income / months_count

    # High value outliers count
    high_value_count = df.get("is_high_value", pd.Series(0, index=df.index)).sum()

    return {
        "total_spend": round(total_spend, 2),
        "total_income": round(total_income, 2),
        "total_transfers": round(total_transfers, 2),
        "net_savings": round(net_savings, 2),
        "savings_rate_pct": round(savings_rate, 2),
        "needs_spend": round(needs_spend, 2),
        "wants_spend": round(wants_spend, 2),
        "discretionary_ratio_pct": round(discretionary_ratio, 2),
        "monthly_burn_rate": round(monthly_burn_rate, 2),
        "monthly_income_avg": round(monthly_income_avg, 2),
        "months_count": months_count,
        "total_transactions": len(df),
        "high_value_transactions": int(high_value_count)
    }

def get_monthly_summary(df):
    """
    Returns monthly time-series of Income, Expense, Net Savings, and Savings Rate.
    """
    summary = df.groupby(["year_month", "transaction_type"])["amount"].sum().unstack(fill_value=0)
    for col in ["Expense", "Income", "Transfer"]:
        if col not in summary.columns:
            summary[col] = 0.0
            
    summary["Net"] = summary["Income"] - summary["Expense"]
    summary["Savings_Rate_Pct"] = np.where(
        summary["Income"] > 0,
        (summary["Net"] / summary["Income"] * 100).round(2),
        0.0
    )
    return summary.reset_index()

def get_50_30_20_breakdown(df):
    """
    Computes percentage allocation across Needs, Wants, and Savings by month.
    Benchmark: 50% Needs, 30% Wants, 20% Savings.
    """
    piv = df.pivot_table(
        index="year_month",
        columns="budget_bucket",
        values="amount",
        aggfunc="sum",
        fill_value=0
    ).reset_index()

    for col in ["Needs", "Wants", "Savings", "Income"]:
        if col not in piv.columns:
            piv[col] = 0.0

    piv["Total_Expenditure"] = piv["Needs"] + piv["Wants"]
    piv["Needs_Pct"] = np.where(piv["Income"] > 0, (piv["Needs"] / piv["Income"] * 100).round(1), 0.0)
    piv["Wants_Pct"] = np.where(piv["Income"] > 0, (piv["Wants"] / piv["Income"] * 100).round(1), 0.0)
    piv["Savings_Pct"] = np.where(piv["Income"] > 0, (piv["Savings"] / piv["Income"] * 100).round(1), 0.0)
    return piv

def get_pareto_merchants(df, top_n=25):
    """
    Performs Pareto (80/20) analysis on vendors/merchants.
    """
    exp_df = df[df["transaction_type"] == "Expense"]
    merchant_spend = exp_df.groupby(["clean_merchant", "category"])["amount"].agg(
        total_spend="sum",
        tx_count="count",
        avg_spend="mean"
    ).reset_index().sort_values(by="total_spend", ascending=False)

    grand_total = merchant_spend["total_spend"].sum()
    merchant_spend["cumulative_spend"] = merchant_spend["total_spend"].cumsum()
    merchant_spend["cumulative_pct"] = (merchant_spend["cumulative_spend"] / grand_total * 100).round(2)
    merchant_spend["pareto_tier"] = np.where(merchant_spend["cumulative_pct"] <= 80.0, "Top 80% (Vital Few)", "Long Tail")
    return merchant_spend.head(top_n)

def detect_anomalies(df, multiplier=2.5):
    """
    Detects unusual transaction outliers using Category-specific IQR thresholds.
    """
    exp_df = df[df["transaction_type"] == "Expense"].copy()
    anomalies = []

    for cat, group in exp_df.groupby("category"):
        q25 = group["amount"].quantile(0.25)
        q75 = group["amount"].quantile(0.75)
        iqr = q75 - q25
        upper_bound = q75 + (multiplier * iqr)
        
        # Don't flag low-value items under $100 as anomalous
        effective_bound = max(upper_bound, 120.0)
        
        outlier_rows = group[group["amount"] > effective_bound].copy()
        if not outlier_rows.empty:
            outlier_rows["category_q75"] = round(q75, 2)
            outlier_rows["threshold_limit"] = round(effective_bound, 2)
            outlier_rows["severity_score"] = ((outlier_rows["amount"] - effective_bound) / (iqr + 1e-5)).round(1)
            anomalies.append(outlier_rows)

    if anomalies:
        anom_df = pd.concat(anomalies).sort_values(by="amount", ascending=False)
        return anom_df
    return pd.DataFrame()

def audit_subscriptions(df):
    """
    Identifies recurring subscriptions and projects 12-month annual cost run-rate.
    """
    sub_df = df[(df["is_recurring"] == 1) & (df["transaction_type"] == "Expense")]
    audit = sub_df.groupby(["clean_merchant", "category", "subcategory"]).agg(
        active_months=("year_month", "nunique"),
        avg_monthly_cost=("amount", "mean"),
        total_lifetime_spent=("amount", "sum"),
        last_charged_date=("date", "max")
    ).reset_index()

    audit["avg_monthly_cost"] = audit["avg_monthly_cost"].round(2)
    audit["total_lifetime_spent"] = audit["total_lifetime_spent"].round(2)
    audit["projected_annual_cost"] = (audit["avg_monthly_cost"] * 12).round(2)
    return audit.sort_values(by="projected_annual_cost", ascending=False)
