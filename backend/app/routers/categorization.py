from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.category_rule import CategoryRule
from backend.app.schemas.analytics import CategorizationSuggestion, CategoryRuleCreate, CategoryRuleOut
from backend.app.services.auth_service import get_current_user
from backend.app.services.categorization_service import suggest_category_for_description, record_user_correction

router = APIRouter(prefix="/categorization", tags=["Smart Categorization"])

class SuggestRequest(BaseModel):
    description: str

@router.post("/suggest", response_model=CategorizationSuggestion)
def suggest_category(
    payload: SuggestRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Predicts category and budget bucket from a description string."""
    return suggest_category_for_description(db, current_user.id, payload.description)

@router.get("/rules", response_model=List[CategoryRuleOut])
def list_user_rules(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lists custom learned rules remembered for the user."""
    rules = (
        db.query(CategoryRule)
        .filter(CategoryRule.user_id == current_user.id)
        .order_by(CategoryRule.priority.desc(), CategoryRule.created_at.desc())
        .all()
    )
    return [CategoryRuleOut.model_validate(r) for r in rules]

@router.post("/rules", response_model=CategoryRuleOut, status_code=status.HTTP_201_CREATED)
def create_custom_rule(
    rule_in: CategoryRuleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    rule = record_user_correction(
        db=db,
        user_id=current_user.id,
        raw_description=rule_in.keyword_pattern,
        category=rule_in.category,
        subcategory=rule_in.subcategory or "",
        budget_bucket=rule_in.budget_bucket or "Wants"
    )
    return CategoryRuleOut.model_validate(rule)

@router.delete("/rules/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_custom_rule(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    rule = db.query(CategoryRule).filter(CategoryRule.id == id, CategoryRule.user_id == current_user.id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found.")
    db.delete(rule)
    db.commit()
    return None
