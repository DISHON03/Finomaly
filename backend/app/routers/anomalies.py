from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.anomaly import AnomalyAlert
from backend.app.schemas.anomaly import AnomalyAlertOut, AnomalyScanResult, AnomalyStatusUpdate
from backend.app.services.auth_service import get_current_user
from backend.app.services.anomaly_service import run_spending_anomaly_scan, update_anomaly_status

router = APIRouter(prefix="/anomalies", tags=["Spending Anomaly Detection"])

@router.get("", response_model=List[AnomalyAlertOut])
def get_anomalies(
    status: Optional[str] = Query(None, description="active, reviewed, dismissed"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(AnomalyAlert).filter(AnomalyAlert.user_id == current_user.id)
    if status and status != "all":
        query = query.filter(AnomalyAlert.status == status)

    alerts = query.order_by(AnomalyAlert.created_at.desc()).limit(100).all()
    results = []
    for a in alerts:
        results.append(AnomalyAlertOut(
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
    return results

@router.post("/scan", response_model=AnomalyScanResult)
def trigger_anomaly_scan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Triggers ML Isolation Forest & Statistical IQR scans to detect new spending anomalies."""
    result = run_spending_anomaly_scan(db, current_user.id)
    return result

@router.patch("/{id}/status", response_model=bool)
def change_anomaly_status(
    id: int,
    status_update: AnomalyStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    success = update_anomaly_status(db, id, current_user.id, status_update.status)
    if not success:
        raise HTTPException(status_code=404, detail="Anomaly alert not found.")
    return True
