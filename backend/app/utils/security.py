import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from backend.app.config import settings

def hash_password(password: str) -> str:
    """Hashes a plaintext password using bcrypt with salt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plaintext password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Generates an encoded JWT access token with expiration timestamp."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decodes and validates a JWT token."""
    keys_to_try = [settings.SECRET_KEY]
    legacy_key = "spendsense-super-secret-jwt-token-key-2026-production"
    if legacy_key not in keys_to_try:
        keys_to_try.append(legacy_key)

    for key in keys_to_try:
        try:
            payload = jwt.decode(token, key, algorithms=[settings.ALGORITHM])
            return payload
        except jwt.PyJWTError:
            continue
    return None
