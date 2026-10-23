from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.user_preference import UserPreference
from backend.app.schemas.auth import UserCreate
from backend.app.utils.security import hash_password, verify_password, decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email.lower().strip()).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, user_in: UserCreate, is_demo: bool = False) -> User:
    hashed_pwd = hash_password(user_in.password)
    user = User(
        email=user_in.email.lower().strip(),
        hashed_password=hashed_pwd,
        full_name=user_in.full_name.strip(),
        is_demo=is_demo
    )
    db.add(user)
    db.flush()
    
    # Initialize default user preferences
    pref = UserPreference(
        user_id=user.id,
        theme="dark",
        currency_symbol="$",
        monthly_savings_target_pct=20.0,
        anomaly_sensitivity="balanced"
    )
    db.add(pref)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user and email.lower().strip() in ("demo@finomaly.io", "demo@spendsense.io"):
        user = db.query(User).filter(User.is_demo == True).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        if user.is_demo and password in ("finomaly123", "spendsense123"):
            return user
        return None
    return user

def get_current_user(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Extracts the authenticated user from the Bearer token.
    If no token is provided, defaults or falls back to the demo user for seamless exploration!
    """
    if token:
        payload = decode_access_token(token)
        if payload and "sub" in payload:
            user_id = int(payload["sub"])
            user = get_user_by_id(db, user_id)
            if user:
                return user

    # Fallback to demo user if available
    demo_user = db.query(User).filter(User.is_demo == True).first()
    if demo_user:
        return demo_user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
