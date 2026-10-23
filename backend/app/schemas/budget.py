from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class BudgetBase(BaseModel):
    category: str
    budget_bucket: str = Field(default="Wants", pattern="^(Needs|Wants|Savings)$")
    monthly_target: float = Field(..., gt=0)
    alert_threshold: Optional[float] = Field(default=80.0, ge=0, le=100)
    year_month: Optional[str] = None

class BudgetCreate(BudgetBase):
    pass

class BudgetUpdate(BaseModel):
    monthly_target: Optional[float] = Field(None, gt=0)
    alert_threshold: Optional[float] = Field(None, ge=0, le=100)
    budget_bucket: Optional[str] = None

class BudgetOut(BudgetBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class BudgetPerformanceItem(BaseModel):
    category: str
    budget_bucket: str
    monthly_target: float
    actual_spent: float
    remaining_amount: float
    utilization_pct: float
    alert_threshold: float
    status: str  # OK, APPROACHING, EXCEEDED

class BudgetSummary(BaseModel):
    year_month: str
    total_budget: float
    total_spent: float
    remaining_total: float
    overall_utilization_pct: float
    needs_spent: float
    needs_budget: float
    wants_spent: float
    wants_budget: float
    savings_allocated: float
    savings_target: float
    items: List[BudgetPerformanceItem]
