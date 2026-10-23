from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class AnomalyAlertBase(BaseModel):
    alert_type: str
    title: str
    explanation: str
    severity: str = "MEDIUM"
    comparison_metric: Optional[str] = None
    difference_amount: Optional[float] = None
    status: str = "active"

class AnomalyAlertOut(AnomalyAlertBase):
    id: int
    user_id: int
    transaction_id: Optional[int] = None
    created_at: datetime
    # Enriched fields from transaction if linked
    transaction_date: Optional[str] = None
    transaction_merchant: Optional[str] = None
    transaction_amount: Optional[float] = None
    transaction_category: Optional[str] = None

    class Config:
        from_attributes = True

class AnomalyStatusUpdate(BaseModel):
    status: str  # reviewed, dismissed, active

class AnomalyScanResult(BaseModel):
    scanned_transactions: int
    new_anomalies_detected: int
    method_used: str  # "Isolation Forest (ML)" or "IQR Statistical Baseline"
    alerts: List[AnomalyAlertOut]
