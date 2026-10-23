import pandas as pd
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.transaction import Transaction
from backend.app.models.budget import Budget
from backend.app.models.anomaly import AnomalyAlert
from backend.app.schemas.analytics import (
    DashboardKPIs, MonthlyTrendPoint, CategoryBreakdownItem, RecentTransactionItem
)
from backend.app.services.auth_service import get_current_user
from backend.app.services.forecast_service import compute_expense_forecast
from backend.app.services.seed_service import reset_demo_data

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/kpis", response_model=DashboardKPIs)
def get_dashboard_kpis(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Transaction).filter(Transaction.user_id == current_user.id)
    if date_from:
        query = query.filter(Transaction.date >= date_from)
    if date_to:
        query = query.filter(Transaction.date <= date_to)
    if category and category != "All":
        query = query.filter(Transaction.category == category)

    txs = query.all()
    if not txs:
        return DashboardKPIs(
            total_income=0.0,
            total_expenses=0.0,
            remaining_balance=0.0,
            savings_rate=0.0,
            needs_spend=0.0,
            wants_spend=0.0,
            savings_alloc=0.0,
            needs_pct=0.0,
            wants_pct=0.0,
            savings_pct=0.0,
            active_anomalies_count=0,
            predicted_eom_spend=0.0,
            budget_target=3500.0,
            currency_symbol="$"
        )

    df = pd.DataFrame([{
        "amount": float(t.amount),
        "type": t.transaction_type,
        "bucket": t.budget_bucket
    } for t in txs])

    total_income = df[df["type"] == "Income"]["amount"].sum()
    total_expenses = df[df["type"] == "Expense"]["amount"].sum()
    remaining_balance = round(total_income - total_expenses, 2)
    savings_rate = round((remaining_balance / total_income * 100), 2) if total_income > 0 else 0.0

    needs_spend = df[(df["type"] == "Expense") & (df["bucket"] == "Needs")]["amount"].sum()
    wants_spend = df[(df["type"] == "Expense") & (df["bucket"] == "Wants")]["amount"].sum()
    savings_alloc = df[(df["type"] == "Transfer") | (df["bucket"] == "Savings")]["amount"].sum()

    needs_pct = round((needs_spend / total_income * 100), 1) if total_income > 0 else 0.0
    wants_pct = round((wants_spend / total_income * 100), 1) if total_income > 0 else 0.0
    savings_pct = round((savings_alloc / total_income * 100), 1) if total_income > 0 else 0.0

    # Active anomalies count
    active_anomalies = (
        db.query(AnomalyAlert)
        .filter(AnomalyAlert.user_id == current_user.id, AnomalyAlert.status == "active")
        .count()
    )

    # Forecast and total budget
    forecast = compute_expense_forecast(db, current_user.id)
    budgets = db.query(Budget).filter(Budget.user_id == current_user.id).all()
    budget_target = sum(b.monthly_target for b in budgets) if budgets else 3500.0

    return DashboardKPIs(
        total_income=round(total_income, 2),
        total_expenses=round(total_expenses, 2),
        remaining_balance=remaining_balance,
        savings_rate=savings_rate,
        needs_spend=round(needs_spend, 2),
        wants_spend=round(wants_spend, 2),
        savings_alloc=round(savings_alloc, 2),
        needs_pct=needs_pct,
        wants_pct=wants_pct,
        savings_pct=savings_pct,
        active_anomalies_count=active_anomalies,
        predicted_eom_spend=forecast.projected_end_of_month,
        budget_target=round(budget_target, 2),
        currency_symbol="$"
    )

@router.get("/trends", response_model=List[MonthlyTrendPoint])
def get_monthly_trends(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    txs = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    if not txs:
        return []

    df = pd.DataFrame([{
        "year_month": t.date[:7],
        "amount": float(t.amount),
        "type": t.transaction_type
    } for t in txs])

    points: List[MonthlyTrendPoint] = []
    for ym, group in df.groupby("year_month"):
        inc = group[group["type"] == "Income"]["amount"].sum()
        exp = group[group["type"] == "Expense"]["amount"].sum()
        net = inc - exp
        rate = round((net / inc * 100), 2) if inc > 0 else 0.0
        points.append(MonthlyTrendPoint(
            year_month=ym,
            income=round(inc, 2),
            expense=round(exp, 2),
            net_savings=round(net, 2),
            savings_rate_pct=rate
        ))

    points.sort(key=lambda x: x.year_month)
    return points[-12:]  # Last 12 months

@router.get("/category-breakdown", response_model=List[CategoryBreakdownItem])
def get_category_breakdown(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_type == "Expense"
    )
    if date_from:
        query = query.filter(Transaction.date >= date_from)
    if date_to:
        query = query.filter(Transaction.date <= date_to)

    txs = query.all()
    if not txs:
        return []

    df = pd.DataFrame([{"category": t.category, "bucket": t.budget_bucket, "amount": float(t.amount)} for t in txs])
    total = df["amount"].sum()

    grouped = df.groupby(["category", "bucket"]).agg(
        amount=("amount", "sum"),
        count=("amount", "count")
    ).reset_index().sort_values("amount", ascending=False)

    items = []
    for _, row in grouped.iterrows():
        pct = round((row["amount"] / total * 100), 1) if total > 0 else 0.0
        items.append(CategoryBreakdownItem(
            category=row["category"],
            budget_bucket=row["bucket"],
            amount=round(row["amount"], 2),
            percentage=pct,
            transaction_count=int(row["count"])
        ))
    return items

@router.get("/recent-transactions", response_model=List[RecentTransactionItem])
def get_recent_transactions(
    limit: int = Query(8, ge=1, le=25),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    txs = (
        db.query(Transaction)
        .filter(Transaction.user_id == current_user.id)
        .order_by(desc(Transaction.date), desc(Transaction.id))
        .limit(limit)
        .all()
    )
    return [
        RecentTransactionItem(
            id=t.id,
            date=t.date,
            clean_merchant=t.clean_merchant,
            amount=t.amount,
            transaction_type=t.transaction_type,
            category=t.category,
            budget_bucket=t.budget_bucket
        )
        for t in txs
    ]

@router.post("/reset-demo")
def reset_demo_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Resets user's account with fresh demo transactions and benchmarks."""
    reset_demo_data(db, current_user.id)
    return {"message": "Demo profile successfully reset with baseline financial transactions."}
