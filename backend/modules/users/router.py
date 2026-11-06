import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies import get_db, require_admin, success_response, paginated_response, AppException
from modules.users.schemas import UserCreate, UserUpdate, UserResponse
from modules.users import service as users_service
from modules.auth.utils import hash_password
from modules.audit import service as audit_service

router = APIRouter()

@router.get("")
async def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin)
):
    """Admin-only endpoint to list all users with pagination."""
    users, total = await users_service.list_users(db, page=page, limit=limit)
    data = [
        UserResponse(
            id=u.id,
            email=u.email,
            role=u.role,
            is_active=u.is_active,
            created_at=u.created_at
        ).model_dump()
        for u in users
    ]
    return paginated_response(data=data, page=page, limit=limit, total=total)

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin)
):
    """Admin-only endpoint to create teacher, guardian, or admin accounts."""
    existing = await users_service.get_user_by_email(db, payload.email)
    if existing:
        raise AppException(
            status_code=status.HTTP_409_CONFLICT,
            code="USER_EMAIL_EXISTS",
            message=f"User with email {payload.email} already exists"
        )

    pwd_hash = hash_password(payload.password)
    user = await users_service.create_user(
        db=db,
        email=payload.email,
        password_hash=pwd_hash,
        role=payload.role
    )

    await audit_service.log_action(
        db=db,
        actor_id=admin.id,
        action=audit_service.USER_CREATED,
        entity_type="user",
        entity_id=user.id,
        old_value=None,
        new_value={"email": user.email, "role": user.role}
    )
    await db.commit()
    await db.refresh(user)

    data = UserResponse(
        id=user.id,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at
    ).model_dump()
    return success_response(data=data, message="User created successfully")

@router.get("/{user_id}")
async def get_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin)
):
    """Admin-only endpoint to retrieve a single user by ID."""
    user = await users_service.get_user_by_id(db, user_id)
    if not user:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            code="USER_NOT_FOUND",
            message="User not found"
        )
    data = UserResponse(
        id=user.id,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at
    ).model_dump()
    return success_response(data=data, message="User retrieved")

@router.put("/{user_id}")
async def update_user(
    user_id: uuid.UUID,
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin)
):
    """Admin-only endpoint to update email or role of a user."""
    user = await users_service.get_user_by_id(db, user_id)
    if not user:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            code="USER_NOT_FOUND",
            message="User not found"
        )

    if payload.email and payload.email != user.email:
        existing = await users_service.get_user_by_email(db, payload.email)
        if existing:
            raise AppException(
                status_code=status.HTTP_409_CONFLICT,
                code="USER_EMAIL_EXISTS",
                message=f"User with email {payload.email} already exists"
            )

    old_val = {"email": user.email, "role": user.role}
    user = await users_service.update_user(db, user, email=payload.email, role=payload.role)
    new_val = {"email": user.email, "role": user.role}

    await audit_service.log_action(
        db=db,
        actor_id=admin.id,
        action="USER_UPDATED",
        entity_type="user",
        entity_id=user.id,
        old_value=old_val,
        new_value=new_val
    )
    await db.commit()
    await db.refresh(user)

    data = UserResponse(
        id=user.id,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at
    ).model_dump()
    return success_response(data=data, message="User updated successfully")

@router.delete("/{user_id}")
async def delete_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin)
):
    """Admin-only endpoint to soft delete a user (sets is_active=False)."""
    user = await users_service.get_user_by_id(db, user_id)
    if not user:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            code="USER_NOT_FOUND",
            message="User not found"
        )

    old_val = {"is_active": user.is_active}
    user = await users_service.soft_delete_user(db, user)
    new_val = {"is_active": user.is_active}

    await audit_service.log_action(
        db=db,
        actor_id=admin.id,
        action=audit_service.USER_DEACTIVATED,
        entity_type="user",
        entity_id=user.id,
        old_value=old_val,
        new_value=new_val
    )
    await db.commit()
    await db.refresh(user)

    return success_response(data={"id": str(user.id), "is_active": user.is_active}, message="User deactivated")

