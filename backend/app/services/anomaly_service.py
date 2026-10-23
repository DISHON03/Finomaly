import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from backend.app.models.transaction import Transaction
from backend.app.models.anomaly import AnomalyAlert
from backend.app.schemas.anomaly import AnomalyScanResult, AnomalyAlertOut

def run_spending_anomaly_scan(db: Session, user_id: int) -> AnomalyScanResult:
    """
    Executes a comprehensive anomaly detection pipeline on user's expenses:
    1. Statistical Baseline (IQR & Category Median/IQR) for all datasets.
    2. scikit-learn Isolation Forest when >= 30 transactions exist.
    3. Category Surge Detection (comparing current month vs previous 3-month trailing average).
    4. Generates data-driven, non-alarmist explanations without falsely claiming fraud.
    """
    # Fetch all expense transactions for user
    tx_query = (
        db.query(Transaction)
        .filter(Transaction.user_id == user_id, Transaction.transaction_type == "Expense")
        .order_by(Transaction.date.asc())
        .all()
    )

    if not tx_query:
        return AnomalyScanResult(
            scanned_transactions=0,
            new_anomalies_detected=0,
            method_used="No expense data",
            alerts=[]
        )

    # Convert to DataFrame
    records = []
    for tx in tx_query:
        records.append({
            "id": tx.id,
            "date": tx.date,
            "clean_merchant": tx.clean_merchant,
            "raw_description": tx.raw_description,
            "amount": float(tx.amount),
            "category": tx.category,
            "subcategory": tx.subcategory or "",
            "budget_bucket": tx.budget_bucket
        })
    df = pd.DataFrame(records)
    df["date_dt"] = pd.to_datetime(df["date"])
    df["year_month"] = df["date_dt"].dt.strftime("%Y-%m")

    # Get already existing alerts for this user to avoid re-alerting
    existing_alerts = db.query(AnomalyAlert).filter(AnomalyAlert.user_id == user_id).all()
    existing_tx_ids = {a.transaction_id for a in existing_alerts if a.transaction_id is not None}
    existing_titles = {a.title for a in existing_alerts}

    new_alerts: List[AnomalyAlert] = []
    method_used = "IQR Statistical Baseline"

    # 1. Isolation Forest (ML) if >= 30 records, else Statistical IQR
    if len(df) >= 30:
        try:
            from sklearn.ensemble import IsolationForest
            method_used = "Isolation Forest (scikit-learn ML) + Category IQR"

            # Compute category medians for relative scaling
            cat_medians = df.groupby("category")["amount"].transform("median")
            df["amount_vs_cat_median"] = df["amount"] / (cat_medians + 1e-2)
            df["log_amount"] = np.log1p(df["amount"])
            df["day_of_week"] = df["date_dt"].dt.dayofweek

            # Feature matrix
            X = df[["log_amount", "amount_vs_cat_median", "day_of_week"]].values

            iso = IsolationForest(contamination=0.035, random_state=42)
            iso.fit(X)
            preds = iso.predict(X)
            ml_outlier_indices = df.index[preds == -1].tolist()
        except Exception:
            ml_outlier_indices = []
            method_used = "IQR Statistical Baseline"
    else:
        ml_outlier_indices = []

    # 2. Category-Specific Statistical Bounds & Explanation Generation
    for cat, group in df.groupby("category"):
        q25 = group["amount"].quantile(0.25)
        q75 = group["amount"].quantile(0.75)
        median = group["amount"].median()
        iqr = q75 - q25
        # Effective threshold: at least $75 and q75 + 2.5 * iqr
        upper_threshold = max(q75 + (2.5 * iqr), median * 2.8, 75.0)

        for idx, row in group.iterrows():
            tx_id = int(row["id"])
            if tx_id in existing_tx_ids:
                continue

            is_stat_outlier = row["amount"] > upper_threshold
            is_ml_outlier = idx in ml_outlier_indices and row["amount"] > (median * 2.0) and row["amount"] >= 60.0

            if is_stat_outlier or is_ml_outlier:
                diff = round(row["amount"] - median, 2)
                multiplier = round(row["amount"] / (median + 1e-2), 1)
                
                # Determine severity
                if multiplier >= 4.0 or diff >= 350.0:
                    severity = "HIGH"
                elif multiplier >= 2.5 or diff >= 150.0:
                    severity = "MEDIUM"
                else:
                    severity = "LOW"

                title = f"Unusual spend at {row['clean_merchant']}"
                explanation = (
                    f"Transaction of ${row['amount']:.2f} is {multiplier}x higher than your median spend "
                    f"of ${median:.2f} for {cat} (+${diff:.2f} difference above your typical baseline)."
                )
                comparison_metric = f"{multiplier}x category median (${median:.2f})"

                alert = AnomalyAlert(
                    user_id=user_id,
                    transaction_id=tx_id,
                    alert_type="AMOUNT_SPIKE",
                    title=title,
                    explanation=explanation,
                    severity=severity,
                    comparison_metric=comparison_metric,
                    difference_amount=diff,
                    status="active"
                )
                db.add(alert)
                new_alerts.append(alert)
                existing_tx_ids.add(tx_id)

    # 3. Category Monthly Surge Detection
    all_months = sorted(df["year_month"].unique())
    if len(all_months) >= 2:
        latest_month = all_months[-1]
        prior_months = all_months[:-1][-3:]  # Trailing 3 months prior

        curr_month_df = df[df["year_month"] == latest_month]
        prior_months_df = df[df["year_month"].isin(prior_months)]

        curr_cat_spend = curr_month_df.groupby("category")["amount"].sum()
        prior_cat_spend = prior_months_df.groupby("category")["amount"].sum() / len(prior_months)

        for cat in curr_cat_spend.index:
            curr_val = curr_cat_spend[cat]
            prior_val = prior_cat_spend.get(cat, 0.0)

            if prior_val > 50.0 and curr_val > 150.0:
                surge_ratio = curr_val / prior_val
                if surge_ratio >= 1.65:
                    surge_diff = round(curr_val - prior_val, 2)
                    pct_increase = round((surge_ratio - 1.0) * 100, 1)
                    surge_title = f"{cat} Monthly Surge ({latest_month})"

                    if surge_title not in existing_titles:
                        surge_alert = AnomalyAlert(
                            user_id=user_id,
                            transaction_id=None,
                            alert_type="CATEGORY_SURGE",
                            title=surge_title,
                            explanation=(
                                f"Total spending in {cat} reached ${curr_val:.2f} in {latest_month}, "
                                f"which is +{pct_increase}% higher than your trailing {len(prior_months)}-month "
                                f"average of ${prior_val:.2f} (+${surge_diff:.2f} variance)."
                            ),
                            severity="HIGH" if surge_ratio >= 2.2 else "MEDIUM",
                            comparison_metric=f"+{pct_increase}% vs trailing avg",
                            difference_amount=surge_diff,
                            status="active"
                        )
                        db.add(surge_alert)
                        new_alerts.append(surge_alert)
                        existing_titles.add(surge_title)

    if new_alerts:
        db.commit()
        for a in new_alerts:
            db.refresh(a)

    # Fetch all active and recent alerts to return
    all_user_alerts = (
        db.query(AnomalyAlert)
        .filter(AnomalyAlert.user_id == user_id)
        .order_by(AnomalyAlert.created_at.desc())
        .limit(50)
        .all()
    )

    enriched_alerts = []
    for a in all_user_alerts:
        enriched_alerts.append(AnomalyAlertOut(
            id=a.id,
            user_id=a.user_id,
            transaction_id=a.transaction_id,
            alert_type=a.alert_type,
            title=a.title,
            explanation=a.explanation,
            severity=a.severity,
            comparison_metric=a.comparison_metric,
            difference_amount=a.difference_amount,
            status=a.status,
            created_at=a.created_at,
            transaction_date=a.transaction.date if a.transaction else None,
            transaction_merchant=a.transaction.clean_merchant if a.transaction else None,
            transaction_amount=float(a.transaction.amount) if a.transaction else None,
            transaction_category=a.transaction.category if a.transaction else None,
        ))

    return AnomalyScanResult(
        scanned_transactions=len(df),
        new_anomalies_detected=len(new_alerts),
        method_used=method_used,
        alerts=enriched_alerts
    )

def update_anomaly_status(db: Session, alert_id: int, user_id: int, new_status: str) -> bool:
    """Updates the status of an anomaly alert (active, reviewed, dismissed)."""
    alert = db.query(AnomalyAlert).filter(AnomalyAlert.id == alert_id, AnomalyAlert.user_id == user_id).first()
    if not alert:
        return False
    alert.status = new_status
    db.commit()
    db.refresh(alert)
    return True
