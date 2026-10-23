import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from backend.app.models.transaction import Transaction
from backend.app.schemas.analytics import RecurringPaymentItem

def detect_recurring_payments(db: Session, user_id: int) -> List[RecurringPaymentItem]:
    """
    Identifies recurring subscriptions and periodic bills:
    - Filters transactions by merchant
    - Measures amount consistency (low standard deviation / CV)
    - Measures date intervals (clustering around ~7 days, ~30 days, or ~365 days)
    - Projects next charge date and annual cash commitment
    """
    tx_query = (
        db.query(Transaction)
        .filter(Transaction.user_id == user_id, Transaction.transaction_type == "Expense")
        .order_by(Transaction.date.asc())
        .all()
    )

    if not tx_query:
        return []

    # Build DataFrame
    records = []
    for tx in tx_query:
        records.append({
            "clean_merchant": tx.clean_merchant,
            "category": tx.category,
            "amount": float(tx.amount),
            "date": tx.date,
            "is_recurring": bool(tx.is_recurring)
        })
    df = pd.DataFrame(records)
    df["date_dt"] = pd.to_datetime(df["date"])

    recurring_candidates: List[RecurringPaymentItem] = []

    # Group by merchant and category
    for (merchant, cat), group in df.groupby(["clean_merchant", "category"]):
        if len(group) < 2 and not group["is_recurring"].any():
            continue

        sorted_group = group.sort_values(by="date_dt")
        amounts = sorted_group["amount"].values
        mean_amt = float(np.mean(amounts))
        std_amt = float(np.std(amounts)) if len(amounts) > 1 else 0.0
        cv = std_amt / (mean_amt + 1e-4)

        # Date intervals
        intervals = sorted_group["date_dt"].diff().dropna().dt.days.values

        # If flagged is_recurring in data or amounts are remarkably consistent
        is_consistent_amt = (cv <= 0.15) or (std_amt <= 4.0)

        frequency = "Monthly"
        interval_days = 30

        if len(intervals) >= 1:
            median_interval = np.median(intervals)
            if 5 <= median_interval <= 10:
                frequency = "Weekly"
                interval_days = 7
            elif 24 <= median_interval <= 38:
                frequency = "Monthly"
                interval_days = 30
            elif 75 <= median_interval <= 105:
                frequency = "Quarterly"
                interval_days = 90
            elif 330 <= median_interval <= 390:
                frequency = "Annual"
                interval_days = 365
            else:
                # If intervals are scattered but flagged recurring
                if group["is_recurring"].any():
                    frequency = "Monthly"
                    interval_days = 30
                else:
                    continue
        elif not group["is_recurring"].any():
            continue

        # If amounts vary drastically without recurring flag, skip
        if not is_consistent_amt and not group["is_recurring"].any():
            continue

        last_date = sorted_group["date_dt"].iloc[-1]
        next_date = last_date + pd.Timedelta(days=interval_days)

        # Annual cost projection
        if frequency == "Weekly":
            annual_multiplier = 52.0
        elif frequency == "Monthly":
            annual_multiplier = 12.0
        elif frequency == "Quarterly":
            annual_multiplier = 4.0
        else:
            annual_multiplier = 1.0

        est_amt = round(float(np.median(amounts)), 2)
        annual_cost = round(est_amt * annual_multiplier, 2)

        recurring_candidates.append(RecurringPaymentItem(
            merchant=merchant,
            category=cat,
            estimated_amount=est_amt,
            observed_frequency=frequency,
            transaction_count=len(group),
            last_payment_date=last_date.strftime("%Y-%m-%d"),
            estimated_next_date=next_date.strftime("%Y-%m-%d"),
            is_confirmed=bool(group["is_recurring"].any()),
            projected_annual_cost=annual_cost
        ))

    # Sort by projected annual cost descending
    recurring_candidates.sort(key=lambda x: x.projected_annual_cost, reverse=True)
    return recurring_candidates
