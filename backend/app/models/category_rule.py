from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime

from backend.app.database import Base

class CategoryRule(Base):
    __tablename__ = "category_rules"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    keyword_pattern = Column(String, nullable=False)  # Lowercase merchant keyword e.g. "starbucks"
    category = Column(String, nullable=False)
    subcategory = Column(String, nullable=True, default="")
    budget_bucket = Column(String, default="Wants")  # Needs, Wants, Savings, Income
    priority = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="category_rules")

    __table_args__ = (
        Index("ix_rule_user_keyword", "user_id", "keyword_pattern"),
    )


