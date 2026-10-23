from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"

class UserBase(BaseModel):
    email: str = Field(..., pattern=EMAIL_REGEX)
    full_name: str

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: str = Field(..., pattern=EMAIL_REGEX)
    password: str

class UserOut(UserBase):
    id: int
    is_demo: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

class TokenPayload(BaseModel):
    sub: Optional[str] = None
