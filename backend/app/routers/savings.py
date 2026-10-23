import pandas as pd
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.savings_goal import SavingsGoal, GoalContribution
from backend.app.schemas.savings import (
    SavingsGoalCreate, SavingsGoalUpdate, SavingsGoalOut,
    ContributionCreate, ContributionOut
)
from backend.app.services.auth_service import get_current_user

router = APIRouter(prefix="/savings", tags=["Savings Goals"])

def enrich_goal(goal: SavingsGoal) -> SavingsGoalOut:
    progress_pct = round((goal.current_amount / goal.target_amount * 100), 1) if goal.target_amount > 0 else 0.0
    remaining = max(0.0, round(goal.target_amount - goal.current_amount, 2))

    # Calculate monthly contribution velocity
    contribs = goal.contributions
    avg_monthly_contrib = 0.0
    projected_date = None

    if contribs:
        c_df = pd.DataFrame([{"amount": c.amount, "date": pd.to_datetime(c.date)} for c in contribs])
        total_contrib = c_df["amount"].sum()
        date_span = (c_df["date"].max() - c_df["date"].min()).days
        months_span = max(1.0, date_span / 30.4)
        avg_monthly_contrib = round(total_contrib / months_span, 2)

        if remaining > 0 and avg_monthly_contrib > 10.0:
            months_to_complete = remaining / avg_monthly_contrib
            proj_dt = datetime.now() + timedelta(days=int(months_to_complete * 30.4))
            projected_date = proj_dt.strftime("%Y-%m-%d")
        elif remaining == 0:
            projected_date = "Completed"

    return SavingsGoalOut(
        id=goal.id,
        user_id=goal.user_id,
        name=goal.name,
        target_amount=goal.target_amount,
        current_amount=round(goal.current_amount, 2),
        target_date=goal.target_date,
        category=goal.category,
        notes=goal.notes,
        is_completed=goal.is_completed or (goal.current_amount >= goal.target_amount),
        created_at=goal.created_at,
        progress_pct=min(100.0, progress_pct),
        remaining_amount=remaining,
        projected_completion_date=projected_date,
        average_monthly_contribution=avg_monthly_contrib,
        contributions=[ContributionOut.model_validate(c) for c in contribs]
    )

@router.get("/goals", response_model=List[SavingsGoalOut])
def get_savings_goals(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    goals = db.query(SavingsGoal).filter(SavingsGoal.user_id == current_user.id).order_by(SavingsGoal.target_date).all()
    return [enrich_goal(g) for g in goals]

@router.post("/goals", response_model=SavingsGoalOut, status_code=status.HTTP_201_CREATED)
def create_savings_goal(
    goal_in: SavingsGoalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    init_dep = goal_in.initial_deposit or 0.0
    goal = SavingsGoal(
        user_id=current_user.id,
        name=goal_in.name,
        target_amount=goal_in.target_amount,
        current_amount=init_dep,
        target_date=goal_in.target_date,
        category=goal_in.category or "General",
        notes=goal_in.notes,
        is_completed=(init_dep >= goal_in.target_amount)
    )
    db.add(goal)
    db.flush()

    if init_dep > 0:
        contrib = GoalContribution(
            goal_id=goal.id,
            user_id=current_user.id,
            amount=init_dep,
            date=datetime.now().strftime("%Y-%m-%d"),
            notes="Initial deposit upon goal creation"
        )
        db.add(contrib)

    db.commit()
    db.refresh(goal)
    return enrich_goal(goal)

@router.put("/goals/{id}", response_model=SavingsGoalOut)
def update_savings_goal(
    id: int,
    goal_in: SavingsGoalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    goal = db.query(SavingsGoal).filter(SavingsGoal.id == id, SavingsGoal.user_id == current_user.id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Savings goal not found.")

    update_data = goal_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(goal, field, val)

    if goal.current_amount >= goal.target_amount:
        goal.is_completed = True

    db.commit()
    db.refresh(goal)
    return enrich_goal(goal)

@router.delete("/goals/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_savings_goal(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    goal = db.query(SavingsGoal).filter(SavingsGoal.id == id, SavingsGoal.user_id == current_user.id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Savings goal not found.")
    db.delete(goal)
    db.commit()
    return None

@router.post("/goals/{id}/contributions", response_model=SavingsGoalOut)
def add_contribution(
    id: int,
    contrib_in: ContributionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    goal = db.query(SavingsGoal).filter(SavingsGoal.id == id, SavingsGoal.user_id == current_user.id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Savings goal not found.")

    contrib = GoalContribution(
        goal_id=goal.id,
        user_id=current_user.id,
        amount=contrib_in.amount,
        date=contrib_in.date,
        notes=contrib_in.notes
    )
    db.add(contrib)
    goal.current_amount += contrib_in.amount
    if goal.current_amount >= goal.target_amount:
        goal.is_completed = True

    db.commit()
    db.refresh(goal)
    return enrich_goal(goal)
