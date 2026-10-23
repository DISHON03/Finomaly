import pandas as pd
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.budget import Budget
from backend.app.models.transaction import Transaction
from backend.app.schemas.budget import (
    BudgetCreate, BudgetUpdate, BudgetOut, BudgetSummary, BudgetPerformanceItem
)
from backend.app.services.auth_service import get_current_user

router = APIRouter(prefix="/budgets", tags=["Budgets"])

@router.get("", response_model=List[BudgetOut])
def get_budgets(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Budget).filter(Budget.user_id == current_user.id).order_by(Budget.category).all()

@router.get("/summary", response_model=BudgetSummary)
def get_budget_summary(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Computes real-time budget utilization, bucket breakdown, and alert statuses for current month."""
    budgets = db.query(Budget).filter(Budget.user_id == current_user.id).all()
    txs = (
        db.query(Transaction)
        .filter(Transaction.user_id == current_user.id)
        .order_by(Transaction.date.desc())
        .all()
    )

    if not txs:
        # Default empty summary
        return BudgetSummary(
            year_month="Current",
            total_budget=sum(b.monthly_target for b in budgets),
            total_spent=0.0,
            remaining_total=sum(b.monthly_target for b in budgets),
            overall_utilization_pct=0.0,
            needs_spent=0.0,
            needs_budget=sum(b.monthly_target for b in budgets if b.budget_bucket == "Needs"),
            wants_spent=0.0,
            wants_budget=sum(b.monthly_target for b in budgets if b.budget_bucket == "Wants"),
            savings_allocated=0.0,
            savings_target=sum(b.monthly_target for b in budgets if b.budget_bucket == "Savings"),
            items=[]
        )

    df_tx = pd.DataFrame([{
        "category": t.category,
        "bucket": t.budget_bucket,
        "amount": float(t.amount),
        "type": t.transaction_type,
        "year_month": t.date[:7]
    } for t in txs])

    latest_ym = df_tx["year_month"].max()
    curr_df = df_tx[df_tx["year_month"] == latest_ym]
    curr_exp = curr_df[curr_df["type"] == "Expense"]
    curr_savings = curr_df[curr_df["type"].isin(["Transfer"]) | (curr_df["bucket"] == "Savings")]

    cat_spent_map = curr_exp.groupby("category")["amount"].sum().to_dict()

    items: List[BudgetPerformanceItem] = []
    total_budget = 0.0
    total_spent = 0.0

    needs_budget = 0.0
    wants_budget = 0.0
    savings_budget = 0.0

    for b in budgets:
        spent = cat_spent_map.get(b.category, 0.0)
        remaining = round(b.monthly_target - spent, 2)
        util_pct = round((spent / b.monthly_target * 100), 1) if b.monthly_target > 0 else 0.0

        if util_pct >= 100.0:
            item_status = "EXCEEDED"
        elif util_pct >= b.alert_threshold:
            item_status = "APPROACHING"
        else:
            item_status = "OK"

        items.append(BudgetPerformanceItem(
            category=b.category,
            budget_bucket=b.budget_bucket,
            monthly_target=round(b.monthly_target, 2),
            actual_spent=round(spent, 2),
            remaining_amount=remaining,
            utilization_pct=util_pct,
            alert_threshold=b.alert_threshold,
            status=item_status
        ))

        total_budget += b.monthly_target
        total_spent += spent

        if b.budget_bucket == "Needs":
            needs_budget += b.monthly_target
        elif b.budget_bucket == "Wants":
            wants_budget += b.monthly_target
        elif b.budget_bucket == "Savings":
            savings_budget += b.monthly_target

    # Sort items by highest utilization
    items.sort(key=lambda x: x.utilization_pct, reverse=True)

    needs_spent = curr_exp[curr_exp["bucket"] == "Needs"]["amount"].sum()
    wants_spent = curr_exp[curr_exp["bucket"] == "Wants"]["amount"].sum()
    savings_alloc = curr_savings["amount"].sum()

    overall_util = round((total_spent / total_budget * 100), 1) if total_budget > 0 else 0.0

    return BudgetSummary(
        year_month=latest_ym,
        total_budget=round(total_budget, 2),
        total_spent=round(total_spent, 2),
        remaining_total=round(total_budget - total_spent, 2),
        overall_utilization_pct=overall_util,
        needs_spent=round(needs_spent, 2),
        needs_budget=round(needs_budget, 2),
        wants_spent=round(wants_spent, 2),
        wants_budget=round(wants_budget, 2),
        savings_allocated=round(savings_alloc, 2),
        savings_target=round(savings_budget, 2),
        items=items
    )

@router.post("", response_model=BudgetOut, status_code=status.HTTP_201_CREATED)
def create_or_update_budget(
    budget_in: BudgetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing = (
        db.query(Budget)
        .filter(Budget.user_id == current_user.id, Budget.category == budget_in.category)
        .first()
    )
    if existing:
        existing.monthly_target = budget_in.monthly_target
        existing.budget_bucket = budget_in.budget_bucket
        existing.alert_threshold = budget_in.alert_threshold or 80.0
        db.commit()
        db.refresh(existing)
        return BudgetOut.model_validate(existing)

    budget = Budget(
        user_id=current_user.id,
        category=budget_in.category,
        budget_bucket=budget_in.budget_bucket,
        monthly_target=budget_in.monthly_target,
        alert_threshold=budget_in.alert_threshold or 80.0,
        year_month=budget_in.year_month
    )
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return BudgetOut.model_validate(budget)

@router.put("/{id}", response_model=BudgetOut)
def update_budget(
    id: int,
    budget_in: BudgetUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    b = db.query(Budget).filter(Budget.id == id, Budget.user_id == current_user.id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Budget not found.")

    update_data = budget_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(b, field, val)

    db.commit()
    db.refresh(b)
    return BudgetOut.model_validate(b)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    b = db.query(Budget).filter(Budget.id == id, Budget.user_id == current_user.id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Budget not found.")
    db.delete(b)
    db.commit()
    return None
