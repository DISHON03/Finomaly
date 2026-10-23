from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime

from backend.app.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    transaction_id = Column(String, index=True, nullable=True)  # External/legacy ID
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    account_id = Column(String, ForeignKey("accounts.account_id"), index=True, nullable=True)
    
    date = Column(String, index=True, nullable=False)  # YYYY-MM-DD
    raw_description = Column(String, nullable=False)
    clean_merchant = Column(String, index=True, nullable=False)
    amount = Column(Float, index=True, nullable=False)
    transaction_type = Column(String, index=True, nullable=False)  # Expense, Income, Transfer
    category = Column(String, index=True, nullable=False)
    subcategory = Column(String, nullable=True, default="")
    budget_bucket = Column(String, index=True, nullable=False)  # Needs, Wants, Savings, Income
    
    is_recurring = Column(Boolean, default=False)
    payment_channel = Column(String, nullable=True, default="Card")
    city = Column(String, nullable=True, default="Online")
    state = Column(String, nullable=True, default="US")
    notes = Column(String, nullable=True)
    is_demo = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="transactions")

    __table_args__ = (
        Index("ix_tx_user_date", "user_id", "date"),
        Index("ix_tx_user_category", "user_id", "category"),
        Index("ix_tx_user_type", "user_id", "transaction_type"),
    )
