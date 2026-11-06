import uuid
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from modules.subjects.model import Subject

async def get_subject_by_id(db: AsyncSession, subject_id: uuid.UUID) -> Subject | None:
    """Retrieves subject by ID."""
    result = await db.execute(select(Subject).where(Subject.id == subject_id))
    return result.scalar_one_or_none()

async def get_subject_by_code(db: AsyncSession, code: str) -> Subject | None:
    """Retrieves subject by unique code."""
    result = await db.execute(select(Subject).where(Subject.code == code))
    return result.scalar_one_or_none()

async def list_subjects(db: AsyncSession) -> Sequence[Subject]:
    """Lists all subjects ordered by name."""
    result = await db.execute(select(Subject).order_by(Subject.name.asc()))
    return result.scalars().all()

async def create_subject(
    db: AsyncSession,
    name: str,
    code: str,
    total_marks: int
) -> Subject:
    """Creates a new subject record."""
    subject = Subject(name=name, code=code, total_marks=total_marks)
    db.add(subject)
    await db.flush()
    return subject

async def update_subject(
    db: AsyncSession,
    subject: Subject,
    name: str | None = None,
    code: str | None = None,
    total_marks: int | None = None
) -> Subject:
    """Updates subject details."""
    if name is not None:
        subject.name = name
    if code is not None:
        subject.code = code
    if total_marks is not None:
        subject.total_marks = total_marks
    await db.flush()
    return subject

async def delete_subject(db: AsyncSession, subject: Subject) -> None:
    """Deletes a subject record."""
    await db.delete(subject)
    await db.flush()

