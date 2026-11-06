import uuid
from typing import Sequence
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from modules.teachers.model import Teacher
from modules.users.model import User

async def get_teacher_by_id(db: AsyncSession, teacher_id: uuid.UUID) -> Teacher | None:
    """Retrieves teacher record by ID."""
    result = await db.execute(select(Teacher).where(Teacher.id == teacher_id))
    return result.scalar_one_or_none()

async def get_teacher_by_user_id(db: AsyncSession, user_id: uuid.UUID) -> Teacher | None:
    """Retrieves teacher record linked to a given user ID."""
    result = await db.execute(select(Teacher).where(Teacher.user_id == user_id))
    return result.scalar_one_or_none()

async def get_teacher_by_code(db: AsyncSession, employee_code: str) -> Teacher | None:
    """Retrieves teacher record by unique employee code."""
    result = await db.execute(select(Teacher).where(Teacher.employee_code == employee_code))
    return result.scalar_one_or_none()

async def list_teachers(
    db: AsyncSession,
    page: int = 1,
    limit: int = 20
) -> tuple[list[dict], int]:
    """Lists teachers with joined user email and pagination."""
    count_query = select(func.count(Teacher.id))
    total = (await db.execute(count_query)).scalar_one()

    offset = (page - 1) * limit
    query = (
        select(Teacher, User.email)
        .join(User, Teacher.user_id == User.id)
        .order_by(Teacher.full_name.asc())
        .offset(offset)
        .limit(limit)
    )
    rows = (await db.execute(query)).all()
    items = [
        {
            "id": t.id,
            "user_id": t.user_id,
            "email": email,
            "full_name": t.full_name,
            "employee_code": t.employee_code,
            "is_active": t.is_active
        }
        for t, email in rows
    ]
    return items, total

async def create_teacher_record(
    db: AsyncSession,
    user_id: uuid.UUID,
    full_name: str,
    employee_code: str
) -> Teacher:
    """Creates teacher record."""
    teacher = Teacher(
        user_id=user_id,
        full_name=full_name,
        employee_code=employee_code,
        is_active=True
    )
    db.add(teacher)
    await db.flush()
    return teacher

async def update_teacher_record(
    db: AsyncSession,
    teacher: Teacher,
    full_name: str | None = None,
    employee_code: str | None = None
) -> Teacher:
    """Updates teacher record details."""
    if full_name is not None:
        teacher.full_name = full_name
    if employee_code is not None:
        teacher.employee_code = employee_code
    await db.flush()
    return teacher

async def soft_delete_teacher_record(db: AsyncSession, teacher: Teacher) -> Teacher:
    """Soft deletes teacher record (sets is_active=False)."""
    teacher.is_active = False
    await db.flush()
    return teacher

