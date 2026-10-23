from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from backend.app.database import Base

class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True, nullable=False)
    theme = Column(String, default="dark")  # dark, light
    currency_symbol = Column(String, default="$")
    monthly_savings_target_pct = Column(Float, default=20.0)
    anomaly_sensitivity = Column(String, default="balanced")  # relaxed, balanced, sensitive
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="preference")
