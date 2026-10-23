from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.schemas.analytics import FinancialInsightItem
from backend.app.services.auth_service import get_current_user
from backend.app.services.insights_service import generate_financial_insights

router = APIRouter(prefix="/insights", tags=["Financial Insights"])

@router.get("", response_model=List[FinancialInsightItem])
def get_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generates verified data-driven financial observations from real transaction records."""
    return generate_financial_insights(db, current_user.id)
