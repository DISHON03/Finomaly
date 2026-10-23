from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.schemas.auth import UserCreate, UserLogin, UserOut, Token
from backend.app.services.auth_service import (
    get_user_by_email, create_user, authenticate_user, get_current_user
)
from backend.app.services.seed_service import seed_demo_data_if_needed, DEMO_EMAIL, DEMO_PASSWORD
from backend.app.utils.security import create_access_token
from backend.app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists."
        )
    user = create_user(db, user_in)
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    return Token(access_token=access_token, user=UserOut.model_validate(user))

@router.post("/login", response_model=Token)
def login(login_in: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, login_in.email, login_in.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password."
        )
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    return Token(access_token=access_token, user=UserOut.model_validate(user))

@router.post("/demo-login", response_model=Token)
def demo_login(db: Session = Depends(get_db)):
    """Logs in instantly with the seeded realistic demo account."""
    demo_user = seed_demo_data_if_needed(db)
    access_token = create_access_token(data={"sub": str(demo_user.id), "email": demo_user.email})
    return Token(access_token=access_token, user=UserOut.model_validate(demo_user))

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return UserOut.model_validate(current_user)
