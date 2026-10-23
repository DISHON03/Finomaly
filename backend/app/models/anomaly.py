from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime

from backend.app.database import Base

class AnomalyAlert(Base):
    __tablename__ = "anomaly_alerts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=True)
    
    alert_type = Column(String, nullable=False)  # AMOUNT_SPIKE, CATEGORY_SURGE, UNUSUAL_CADENCE, FREQUENCY_ANOMALY
    title = Column(String, nullable=False)
    explanation = Column(String, nullable=False)
    severity = Column(String, default="MEDIUM")  # LOW, MEDIUM, HIGH
    comparison_metric = Column(String, nullable=True)  # e.g. "3.5x category median ($42.00)"
    difference_amount = Column(Float, nullable=True)  # e.g. 210.50 above baseline
    status = Column(String, default="active")  # active, reviewed, dismissed
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="anomaly_alerts")
    transaction = relationship("Transaction")

    __table_args__ = (
        Index("ix_anomaly_user_status", "user_id", "status"),
    )
