from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.schemas.analytics import ForecastSummary
from backend.app.services.auth_service import get_current_user
from backend.app.services.forecast_service import compute_expense_forecast

router = APIRouter(prefix="/forecasting", tags=["Expense Forecasting"])

@router.get("", response_model=ForecastSummary)
def get_expense_forecast(
    horizon: int = Query(4, ge=1, le=12, description="Months forward to project"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Computes end-of-month projected expenses and forward multi-month trajectory
    using Double Exponential Smoothing (Holt's Linear Trend) with confidence intervals.
    """
    return compute_expense_forecast(db, current_user.id, horizon_months=horizon)
