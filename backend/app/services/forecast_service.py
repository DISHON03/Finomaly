import calendar
from datetime import datetime
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from backend.app.models.transaction import Transaction
from backend.app.models.budget import Budget
from backend.app.schemas.analytics import ForecastSummary, ForecastPoint

def compute_expense_forecast(db: Session, user_id: int, horizon_months: int = 4) -> ForecastSummary:
    """
    Computes:
    1. Current End-of-Month (EOM) spend projection using daily burn velocity.
    2. Multi-month forward projections using Double Exponential Smoothing (Holt's Linear Trend) or baseline.
    3. Comparison against active budget target.
    4. 95% Confidence Intervals and explicit limitations notice.
    """
    # Fetch all expense transactions for the user
    tx_query = (
        db.query(Transaction)
        .filter(Transaction.user_id == user_id, Transaction.transaction_type == "Expense")
        .order_by(Transaction.date.asc())
        .all()
    )

    # Fetch user's total budget target
    user_budgets = db.query(Budget).filter(Budget.user_id == user_id).all()
    total_budget_target = sum(b.monthly_target for b in user_budgets) if user_budgets else 3500.0

    if not tx_query:
        # Fallback default empty summary
        now = datetime.now()
        curr_ym = now.strftime("%Y-%m")
        return ForecastSummary(
            model_name="Baseline (Zero Historical Records)",
            historical_months_used=0,
            current_month_to_date=0.0,
            projected_end_of_month=0.0,
            current_monthly_budget=round(total_budget_target, 2),
            budget_variance=0.0,
            status="ON_TRACK",
            limitations_note="No transaction records recorded yet. Start logging expenses to enable forecasting.",
            forward_projections=[]
        )

    # Convert to DataFrame
    df = pd.DataFrame([{
        "date": tx.date,
        "amount": float(tx.amount),
        "year_month": tx.date[:7]
    } for tx in tx_query])
    
    df["date_parsed"] = pd.to_datetime(df["date"])
    
    # Identify latest active month in the data
    latest_date = df["date_parsed"].max()
    latest_ym = latest_date.strftime("%Y-%m")
    
    # Days in latest month
    year = latest_date.year
    month = latest_date.month
    _, total_days_in_month = calendar.monthrange(year, month)
    days_elapsed = max(latest_date.day, 1)

    # Spend to date in latest month
    curr_month_df = df[df["year_month"] == latest_ym]
    curr_month_spend = curr_month_df["amount"].sum()

    # Daily burn rate extrapolation for EOM
    daily_burn_rate = curr_month_spend / days_elapsed
    days_remaining = max(0, total_days_in_month - days_elapsed)
    projected_eom = round(curr_month_spend + (daily_burn_rate * days_remaining), 2)

    # Historical monthly time series
    monthly_series = df.groupby("year_month")["amount"].sum().reset_index()
    monthly_series["date_parsed"] = pd.to_datetime(monthly_series["year_month"] + "-01")
    monthly_series = monthly_series.sort_values(by="date_parsed").reset_index(drop=True)

    n_months = len(monthly_series)
    forward_points: List[ForecastPoint] = []
    
    # Include recent historical points for context (up to last 6 months)
    for _, row in monthly_series.tail(6).iterrows():
        forward_points.append(ForecastPoint(
            period=row["year_month"],
            actual_spend=round(row["amount"], 2),
            forecast_spend=round(row["amount"], 2),
            lower_bound=round(row["amount"], 2),
            upper_bound=round(row["amount"], 2),
            is_forecast=False
        ))

    # Forecasting Engine Selection
    if n_months < 3:
        # Simple moving average baseline
        model_name = "Simple Moving Average Baseline"
        mean_spend = float(monthly_series["amount"].mean())
        std_spend = float(monthly_series["amount"].std()) if n_months > 1 else mean_spend * 0.15

        last_date = monthly_series["date_parsed"].iloc[-1]
        for h in range(1, horizon_months + 1):
            future_date = last_date + pd.DateOffset(months=h)
            future_ym = future_date.strftime("%Y-%m")
            margin = round(1.96 * std_spend * np.sqrt(h), 2)
            
            forward_points.append(ForecastPoint(
                period=future_ym,
                actual_spend=None,
                forecast_spend=round(mean_spend, 2),
                lower_bound=max(0, round(mean_spend - margin, 2)),
                upper_bound=round(mean_spend + margin, 2),
                is_forecast=True
            ))
    else:
        # Holt's Linear Trend (Double Exponential Smoothing)
        model_name = "Holt's Linear Trend (Double Exponential Smoothing)"
        alpha = 0.35
        beta = 0.15
        y = monthly_series["amount"].values
        
        # Initialization
        level = y[0]
        trend = y[1] - y[0] if len(y) > 1 else 0.0
        fitted = [level + trend]

        for t in range(1, len(y)):
            val = y[t]
            last_level = level
            last_trend = trend
            level = alpha * val + (1.0 - alpha) * (last_level + last_trend)
            trend = beta * (level - last_level) + (1.0 - beta) * last_trend
            fitted.append(level + trend)

        residuals = y - np.array(fitted)
        sigma = float(np.std(residuals)) if len(residuals) > 1 else float(np.mean(y) * 0.1)

        last_date = monthly_series["date_parsed"].iloc[-1]
        for h in range(1, horizon_months + 1):
            future_date = last_date + pd.DateOffset(months=h)
            future_ym = future_date.strftime("%Y-%m")
            pred_val = round(level + (h * trend), 2)
            pred_val = max(100.0, pred_val)  # Floor at sensible level

            margin = round(1.96 * sigma * np.sqrt(h), 2)
            lower_bound = max(0.0, round(pred_val - margin, 2))
            upper_bound = round(pred_val + margin, 2)

            forward_points.append(ForecastPoint(
                period=future_ym,
                actual_spend=None,
                forecast_spend=pred_val,
                lower_bound=lower_bound,
                upper_bound=upper_bound,
                is_forecast=True
            ))

    # Budget variance & status
    budget_variance = round(projected_eom - total_budget_target, 2)
    if budget_variance > 100:
        status = "OVER_BUDGET"
    elif budget_variance > -150:
        status = "AT_RISK"
    else:
        status = "ON_TRACK"

    limitations = (
        "Statistical estimates generated via Holt's Linear Trend with 95% confidence intervals. "
        "Forecasts rely strictly on observed historical cadence and spend velocity. "
        "They do not account for external macroeconomic shifts, emergencies, or deliberate lifestyle changes. "
        "Always treat projections as directional planning guidance rather than guaranteed financial outcomes."
    )

    return ForecastSummary(
        model_name=model_name,
        historical_months_used=n_months,
        current_month_to_date=round(curr_month_spend, 2),
        projected_end_of_month=projected_eom,
        current_monthly_budget=round(total_budget_target, 2),
        budget_variance=budget_variance,
        status=status,
        limitations_note=limitations,
        forward_projections=forward_points
    )
