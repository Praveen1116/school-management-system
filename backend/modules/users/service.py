import uuid
from typing import Sequence
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from modules.users.model import User

async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Retrieves a user by email."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> User | None:
    """Retrieves a user by ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

async def list_users(
    db: AsyncSession,
    page: int = 1,
    limit: int = 20,
    role: str | None = None
) -> tuple[Sequence[User], int]:
    """Lists users with pagination and optional role filter."""
    offset = (page - 1) * limit
    count_query = select(func.count(User.id))
    if role:
        count_query = count_query.where(User.role == role)
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    query = select(User).order_by(User.created_at.desc())
    if role:
        query = query.where(User.role == role)
    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    users = result.scalars().all()
    return users, total

async def create_user(
    db: AsyncSession,
    email: str,
    password_hash: str,
    role: str,
    full_name: str | None = None
) -> User:
    """Creates a new user record."""
    user = User(
        email=email,
        password_hash=password_hash,
        role=role,
        full_name=full_name,
        is_active=True
    )
    db.add(user)
    await db.flush()
    return user

async def update_user(
    db: AsyncSession,
    user: User,
    email: str | None = None,
    role: str | None = None,
    full_name: str | None = None
) -> User:
    """Updates user email, role, or full_name."""
    if email is not None:
        user.email = email
    if role is not None:
        user.role = role
    if full_name is not None:
        user.full_name = full_name
    await db.flush()
    return user

async def soft_delete_user(db: AsyncSession, user: User) -> User:
    """Soft deletes a user by setting is_active to False."""
    user.is_active = False
    await db.flush()
    return user

