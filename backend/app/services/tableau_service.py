import io
import os
import pandas as pd
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from backend.app.models.transaction import Transaction
from backend.app.models.budget import Budget
from backend.app.models.anomaly import AnomalyAlert
from backend.app.services.forecast_service import compute_expense_forecast

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
TABLEAU_EXPORT_DIR = os.path.join(BASE_DIR, "tableau", "exports")

def ensure_tableau_dirs():
    os.makedirs(TABLEAU_EXPORT_DIR, exist_ok=True)

def generate_tableau_transactions_csv(db: Session, user_id: int) -> str:
    """Generates clean, Tableau-ready transaction feed with temporal & dimensional enrichments."""
    txs = db.query(Transaction).filter(Transaction.user_id == user_id).order_by(Transaction.date.asc()).all()
    if not txs:
        return "transaction_id,date,clean_merchant,amount,transaction_type,category,subcategory,budget_bucket,is_recurring,payment_channel,city,state,year,month,year_month,day_name,is_weekend\n"

    rows = []
    for tx in txs:
        dt = pd.to_datetime(tx.date)
        rows.append({
            "transaction_id": tx.transaction_id or f"TX_{tx.id}",
            "date": tx.date,
            "clean_merchant": tx.clean_merchant,
            "amount": round(float(tx.amount), 2),
            "transaction_type": tx.transaction_type,
            "category": tx.category,
            "subcategory": tx.subcategory or "",
            "budget_bucket": tx.budget_bucket,
            "is_recurring": "Yes" if tx.is_recurring else "No",
            "payment_channel": tx.payment_channel or "Card",
            "city": tx.city or "Online",
            "state": tx.state or "US",
            "year": dt.year,
            "month": dt.month,
            "year_month": dt.strftime("%Y-%m"),
            "day_name": dt.day_name(),
            "is_weekend": "Weekend" if dt.weekday() >= 5 else "Weekday"
        })
    df = pd.DataFrame(rows)
    return df.to_csv(index=False)

def generate_tableau_monthly_summary_csv(db: Session, user_id: int) -> str:
    """Generates monthly financial rollups (Income, Expense, Net Savings, Savings Rate, 50/30/20 compliance)."""
    txs = db.query(Transaction).filter(Transaction.user_id == user_id).all()
    if not txs:
        return "year_month,total_income,total_expense,net_cashflow,savings_rate_pct,needs_spend,wants_spend,needs_pct,wants_pct,savings_pct\n"

    rows = [{"year_month": tx.date[:7], "amount": float(tx.amount), "type": tx.transaction_type, "bucket": tx.budget_bucket} for tx in txs]
    df = pd.DataFrame(rows)

    monthly_records = []
    for ym, group in df.groupby("year_month"):
        inc = group[group["type"] == "Income"]["amount"].sum()
        exp = group[group["type"] == "Expense"]["amount"].sum()
        net = inc - exp
        savings_rate = round((net / inc * 100), 2) if inc > 0 else 0.0

        needs = group[(group["type"] == "Expense") & (group["bucket"] == "Needs")]["amount"].sum()
        wants = group[(group["type"] == "Expense") & (group["bucket"] == "Wants")]["amount"].sum()
        
        needs_pct = round((needs / inc * 100), 1) if inc > 0 else 0.0
        wants_pct = round((wants / inc * 100), 1) if inc > 0 else 0.0
        savings_pct = round((max(0.0, net) / inc * 100), 1) if inc > 0 else 0.0

        monthly_records.append({
            "year_month": ym,
            "total_income": round(inc, 2),
            "total_expense": round(exp, 2),
            "net_cashflow": round(net, 2),
            "savings_rate_pct": savings_rate,
            "needs_spend": round(needs, 2),
            "wants_spend": round(wants, 2),
            "needs_pct": needs_pct,
            "wants_pct": wants_pct,
            "savings_pct": savings_pct
        })
    
    out_df = pd.DataFrame(monthly_records).sort_values("year_month")
    return out_df.to_csv(index=False)

def generate_tableau_category_expenses_csv(db: Session, user_id: int) -> str:
    """Generates category-level expenditure breakdown with totals and proportions."""
    txs = db.query(Transaction).filter(Transaction.user_id == user_id, Transaction.transaction_type == "Expense").all()
    if not txs:
        return "category,budget_bucket,total_spend,transaction_count,avg_ticket_size,pct_of_total_spend\n"

    rows = [{"category": tx.category, "budget_bucket": tx.budget_bucket, "amount": float(tx.amount)} for tx in txs]
    df = pd.DataFrame(rows)
    total_all = df["amount"].sum()

    cat_df = df.groupby(["category", "budget_bucket"]).agg(
        total_spend=("amount", "sum"),
        transaction_count=("amount", "count"),
        avg_ticket_size=("amount", "mean")
    ).reset_index()

    cat_df["total_spend"] = cat_df["total_spend"].round(2)
    cat_df["avg_ticket_size"] = cat_df["avg_ticket_size"].round(2)
    cat_df["pct_of_total_spend"] = ((cat_df["total_spend"] / total_all) * 100).round(2) if total_all > 0 else 0.0
    cat_df = cat_df.sort_values("total_spend", ascending=False)
    return cat_df.to_csv(index=False)

def generate_tableau_budget_vs_actual_csv(db: Session, user_id: int) -> str:
    """Generates category budget performance, utilization, and variance for Tableau."""
    budgets = db.query(Budget).filter(Budget.user_id == user_id).all()
    txs = db.query(Transaction).filter(Transaction.user_id == user_id, Transaction.transaction_type == "Expense").all()
    
    if not txs:
        return "category,budget_bucket,monthly_target,actual_spent,remaining_budget,utilization_pct,performance_status\n"

    budget_map = {b.category: (b.monthly_target, b.budget_bucket, b.alert_threshold) for b in budgets}
    
    # Calculate spend per category across the latest active month
    df_tx = pd.DataFrame([{"category": t.category, "bucket": t.budget_bucket, "amount": float(t.amount), "year_month": t.date[:7]} for t in txs])
    latest_ym = df_tx["year_month"].max()
    curr_df = df_tx[df_tx["year_month"] == latest_ym]
    
    actual_spent = curr_df.groupby("category")["amount"].sum().to_dict()
    all_cats = set(list(budget_map.keys()) + list(actual_spent.keys()))

    rows = []
    for cat in sorted(all_cats):
        target, bucket, thresh = budget_map.get(cat, (250.0, "Wants", 80.0))
        spent = actual_spent.get(cat, 0.0)
        remaining = round(target - spent, 2)
        util_pct = round((spent / target * 100), 1) if target > 0 else 100.0
        
        if util_pct > 100.0:
            status = "EXCEEDED"
        elif util_pct >= thresh:
            status = "APPROACHING"
        else:
            status = "HEALTHY"

        rows.append({
            "year_month": latest_ym,
            "category": cat,
            "budget_bucket": bucket,
            "monthly_target": round(target, 2),
            "actual_spent": round(spent, 2),
            "remaining_budget": remaining,
            "utilization_pct": util_pct,
            "performance_status": status
        })

    return pd.DataFrame(rows).to_csv(index=False)

def generate_tableau_anomalies_csv(db: Session, user_id: int) -> str:
    """Generates anomaly alerts with linked transaction details for Tableau inspection."""
    alerts = db.query(AnomalyAlert).filter(AnomalyAlert.user_id == user_id).order_by(AnomalyAlert.created_at.desc()).all()
    if not alerts:
        return "alert_id,date,clean_merchant,amount,category,alert_type,severity,comparison_metric,difference_amount,status,explanation\n"

    rows = []
    for a in alerts:
        rows.append({
            "alert_id": a.id,
            "date": a.transaction.date if a.transaction else a.created_at.strftime("%Y-%m-%d"),
            "clean_merchant": a.transaction.clean_merchant if a.transaction else "Category Aggregate",
            "amount": round(float(a.transaction.amount), 2) if a.transaction else 0.0,
            "category": a.transaction.category if a.transaction else a.title.split()[0],
            "alert_type": a.alert_type,
            "severity": a.severity,
            "comparison_metric": a.comparison_metric or "",
            "difference_amount": round(float(a.difference_amount or 0.0), 2),
            "status": a.status,
            "explanation": a.explanation
        })
    return pd.DataFrame(rows).to_csv(index=False)

def generate_tableau_forecast_csv(db: Session, user_id: int) -> str:
    """Generates actual vs forecast timeline with 95% confidence bands for Tableau."""
    forecast = compute_expense_forecast(db, user_id, horizon_months=6)
    rows = []
    for p in forecast.forward_projections:
        rows.append({
            "period": p.period,
            "actual_spend": p.actual_spend if p.actual_spend is not None else "",
            "forecast_spend": p.forecast_spend,
            "lower_bound_95": p.lower_bound,
            "upper_bound_95": p.upper_bound,
            "is_forecast": "Forecast" if p.is_forecast else "Actual",
            "model_used": forecast.model_name
        })
    return pd.DataFrame(rows).to_csv(index=False)

def export_all_tableau_files(db: Session, user_id: int):
    """Exports all 6 reporting CSV datasets to the tableau/exports folder."""
    ensure_tableau_dirs()
    datasets = {
        "transactions_tableau.csv": generate_tableau_transactions_csv(db, user_id),
        "monthly_financial_summaries_tableau.csv": generate_tableau_monthly_summary_csv(db, user_id),
        "category_expenses_tableau.csv": generate_tableau_category_expenses_csv(db, user_id),
        "budget_vs_actual_tableau.csv": generate_tableau_budget_vs_actual_csv(db, user_id),
        "spending_anomalies_tableau.csv": generate_tableau_anomalies_csv(db, user_id),
        "forecast_vs_actual_tableau.csv": generate_tableau_forecast_csv(db, user_id),
    }
    for filename, content in datasets.items():
        filepath = os.path.join(TABLEAU_EXPORT_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
