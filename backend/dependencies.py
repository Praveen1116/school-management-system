import uuid
from typing import Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from modules.auth.service import decode_access_token
from modules.users import service as users_service

# HTTPBearer scheme for JWT bearer token
security = HTTPBearer(auto_error=False)

class AppException(HTTPException):
    """Custom application exception with structured error code and message."""
    def __init__(self, status_code: int, code: str, message: str):
        super().__init__(
            status_code=status_code,
            detail={"code": code, "message": message}
        )
        self.code = code
        self.message = message


def success_response(data: Any = None, message: str = "Done") -> dict:
    """Standard success response shape: {success: true, data: {}, message: 'Done'}"""
    return {
        "success": True,
        "data": data if data is not None else {},
        "message": message
    }


def error_response(code: str, message: str) -> dict:
    """Standard error response shape: {success: false, error: {code: '...', message: '...'}}"""
    return {
        "success": False,
        "error": {
            "code": code,
            "message": message
        }
    }


def paginated_response(data: list, page: int, limit: int, total: int) -> dict:
    """Standard paginated response shape."""
    pages = (total + limit - 1) // limit if limit > 0 else 0
    return {
        "success": True,
        "data": data,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": pages
        }
    }


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Decodes token, loads active user, raises 401 if invalid or 403 if inactive."""
    if not credentials or not credentials.credentials:
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="UNAUTHORIZED",
            message="Could not validate credentials"
        )

    token = credentials.credentials.strip().strip('"').strip("'")
    if token.lower().startswith("bearer "):
        token = token[7:].strip()

    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="INVALID_TOKEN",
            message="Could not validate credentials"
        )

    try:
        user_id = uuid.UUID(payload["sub"])
    except (ValueError, TypeError):
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="INVALID_TOKEN",
            message="Invalid user identifier in token"
        )

    user = await users_service.get_user_by_id(db, user_id)
    if not user:
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="USER_NOT_FOUND",
            message="User not found"
        )

    if not user.is_active:
        raise AppException(
            status_code=status.HTTP_403_FORBIDDEN,
            code="USER_INACTIVE",
            message="User account is deactivated"
        )

    return user


async def require_admin(user=Depends(get_current_user)):
    """Requires the authenticated user to have role 'admin'."""
    if user.role != "admin":
        raise AppException(
            status_code=status.HTTP_403_FORBIDDEN,
            code="FORBIDDEN_ADMIN_ONLY",
            message="Administrative access required"
        )
    return user


async def require_teacher(user=Depends(get_current_user)):
    """Requires the authenticated user to be an admin or teacher."""
    if user.role not in ["admin", "teacher"]:
        raise AppException(
            status_code=status.HTTP_403_FORBIDDEN,
            code="FORBIDDEN_TEACHER_ONLY",
            message="Teacher access required"
        )
    return user


async def require_guardian(user=Depends(get_current_user)):
    """Requires the authenticated user to be an admin or guardian."""
    if user.role not in ["admin", "guardian"]:
        raise AppException(
            status_code=status.HTTP_403_FORBIDDEN,
            code="FORBIDDEN_GUARDIAN_ONLY",
            message="Guardian access required"
        )
    return user

