from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ContributionBase(BaseModel):
    amount: float = Field(..., gt=0)
    date: str = Field(..., description="YYYY-MM-DD")
    notes: Optional[str] = None

class ContributionCreate(ContributionBase):
    pass

class ContributionOut(ContributionBase):
    id: int
    goal_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class SavingsGoalBase(BaseModel):
    name: str
    target_amount: float = Field(..., gt=0)
    target_date: str = Field(..., description="Target completion date YYYY-MM-DD")
    category: Optional[str] = "General"
    notes: Optional[str] = None

class SavingsGoalCreate(SavingsGoalBase):
    initial_deposit: Optional[float] = 0.0

class SavingsGoalUpdate(BaseModel):
    name: Optional[str] = None
    target_amount: Optional[float] = Field(None, gt=0)
    target_date: Optional[str] = None
    category: Optional[str] = None
    notes: Optional[str] = None
    is_completed: Optional[bool] = None

class SavingsGoalOut(SavingsGoalBase):
    id: int
    user_id: int
    current_amount: float
    is_completed: bool
    created_at: datetime
    progress_pct: float
    remaining_amount: float
    projected_completion_date: Optional[str] = None
    average_monthly_contribution: float
    contributions: List[ContributionOut] = []

    class Config:
        from_attributes = True
