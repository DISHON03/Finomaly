from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class TransactionBase(BaseModel):
    date: str = Field(..., description="Date formatted as YYYY-MM-DD")
    raw_description: str
    clean_merchant: Optional[str] = None
    amount: float = Field(..., gt=0, description="Positive transaction amount")
    transaction_type: str = Field(..., pattern="^(Expense|Income|Transfer)$")
    category: str
    subcategory: Optional[str] = ""
    budget_bucket: Optional[str] = "Wants"
    is_recurring: Optional[bool] = False
    payment_channel: Optional[str] = "Card"
    city: Optional[str] = "Online"
    state: Optional[str] = "US"
    notes: Optional[str] = None
    account_id: Optional[str] = None

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    date: Optional[str] = None
    raw_description: Optional[str] = None
    clean_merchant: Optional[str] = None
    amount: Optional[float] = Field(None, gt=0)
    transaction_type: Optional[str] = Field(None, pattern="^(Expense|Income|Transfer)$")
    category: Optional[str] = None
    subcategory: Optional[str] = None
    budget_bucket: Optional[str] = None
    is_recurring: Optional[bool] = None
    payment_channel: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    notes: Optional[str] = None
    account_id: Optional[str] = None

class TransactionOut(TransactionBase):
    id: int
    transaction_id: Optional[str] = None
    user_id: int
    is_demo: bool
    created_at: datetime

    class Config:
        from_attributes = True

class TransactionListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    transactions: List[TransactionOut]

class CSVImportResult(BaseModel):
    total_rows: int
    imported: int
    skipped_duplicates: int
    errors: List[str]
