from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime

from backend.app.database import Base

class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    category = Column(String, index=True, nullable=False)
    budget_bucket = Column(String, nullable=False)  # Needs, Wants, Savings
    monthly_target = Column(Float, nullable=False)
    alert_threshold = Column(Float, default=80.0)  # Percentage warning threshold
    year_month = Column(String, nullable=True)  # Null means recurring global monthly target
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="budgets")

    __table_args__ = (
        Index("ix_budget_user_cat", "user_id", "category"),
    )
