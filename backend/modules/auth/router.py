from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies import get_db, get_current_user, success_response, AppException
from modules.auth.schemas import LoginRequest, TokenResponse, CurrentUserResponse
from modules.auth.service import authenticate_user, create_access_token

router = APIRouter()

@router.post("/login")
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Authenticates credentials and returns a signed JWT access token."""
    user = await authenticate_user(payload.email, payload.password, db)
    if not user:
        # Never specify whether email or password was incorrect (security best practice)
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="INVALID_CREDENTIALS",
            message="Invalid credentials"
        )

    if not user.is_active:
        raise AppException(
            status_code=status.HTTP_403_FORBIDDEN,
            code="USER_INACTIVE",
            message="User account is deactivated"
        )

    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    token_data = TokenResponse(access_token=access_token, token_type="bearer").model_dump()
    return success_response(data=token_data, message="Login successful")

@router.get("/me")
async def get_me(current_user = Depends(get_current_user)):
    """Returns currently authenticated user profile information."""
    user_data = CurrentUserResponse(
        id=current_user.id,
        email=current_user.email,
        role=current_user.role
    ).model_dump()
    return success_response(data=user_data, message="User profile retrieved")

