from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class DashboardKPIs(BaseModel):
    total_income: float
    total_expenses: float
    remaining_balance: float
    savings_rate: float
    needs_spend: float
    wants_spend: float
    savings_alloc: float
    needs_pct: float
    wants_pct: float
    savings_pct: float
    active_anomalies_count: int
    predicted_eom_spend: float
    budget_target: float
    currency_symbol: str = "$"

class MonthlyTrendPoint(BaseModel):
    year_month: str
    income: float
    expense: float
    net_savings: float
    savings_rate_pct: float

class CategoryBreakdownItem(BaseModel):
    category: str
    budget_bucket: str
    amount: float
    percentage: float
    transaction_count: int

class RecentTransactionItem(BaseModel):
    id: int
    date: str
    clean_merchant: str
    amount: float
    transaction_type: str
    category: str
    budget_bucket: str

class ForecastPoint(BaseModel):
    period: str  # Month or date
    actual_spend: Optional[float] = None
    forecast_spend: float
    lower_bound: float
    upper_bound: float
    is_forecast: bool

class ForecastSummary(BaseModel):
    model_name: str
    historical_months_used: int
    current_month_to_date: float
    projected_end_of_month: float
    current_monthly_budget: float
    budget_variance: float
    status: str  # ON_TRACK, AT_RISK, OVER_BUDGET
    limitations_note: str
    forward_projections: List[ForecastPoint]

class RecurringPaymentItem(BaseModel):
    merchant: str
    category: str
    estimated_amount: float
    observed_frequency: str  # Monthly, Weekly, Annual
    transaction_count: int
    last_payment_date: str
    estimated_next_date: str
    is_confirmed: bool = False
    projected_annual_cost: float

class FinancialInsightItem(BaseModel):
    id: str
    type: str  # positive, warning, neutral, tip
    title: str
    observation: str
    metric_highlight: str
    category: Optional[str] = None

class CategorizationSuggestion(BaseModel):
    suggested_category: str
    suggested_subcategory: str
    suggested_budget_bucket: str
    confidence: float
    matched_rule: Optional[str] = None

class CategoryRuleCreate(BaseModel):
    keyword_pattern: str
    category: str
    subcategory: Optional[str] = ""
    budget_bucket: Optional[str] = "Wants"

class CategoryRuleOut(CategoryRuleCreate):
    id: int
    user_id: int

    class Config:
        from_attributes = True
