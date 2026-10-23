from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime

from backend.app.database import Base

class Account(Base):
    __tablename__ = "accounts"

    account_id = Column(String, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # Checking, Savings, Credit Card, Investment
    balance = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
