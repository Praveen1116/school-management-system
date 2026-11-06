import jwt
from datetime import datetime, timezone, timedelta
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from config import settings
from modules.auth.utils import verify_password
from modules.users import service as users_service

async def authenticate_user(email: str, password: str, db: AsyncSession) -> Any | None:
    """Authenticates a user via email and plain password against bcrypt hash."""
    user = await users_service.get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

def create_access_token(data: dict) -> str:
    """Creates a signed JWT token with sub, role, and expiration."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_access_token(token: str) -> dict | None:
    """Decodes and validates a JWT token. Returns None on any error."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except Exception:
        return None

