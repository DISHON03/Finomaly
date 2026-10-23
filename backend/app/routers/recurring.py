from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.schemas.analytics import RecurringPaymentItem
from backend.app.services.auth_service import get_current_user
from backend.app.services.recurring_service import detect_recurring_payments

router = APIRouter(prefix="/recurring", tags=["Recurring Payments"])

@router.get("", response_model=List[RecurringPaymentItem])
def get_recurring_payments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Detects recurring subscriptions, bill cadences, and projected annual commitments."""
    return detect_recurring_payments(db, current_user.id)
