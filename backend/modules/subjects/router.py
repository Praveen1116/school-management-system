import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies import (
    get_db,
    require_admin,
    require_teacher,
    success_response,
    AppException
)
from modules.subjects.schemas import SubjectCreate, SubjectUpdate, SubjectResponse
from modules.subjects import service as subjects_service

router = APIRouter()

@router.get("")
async def list_subjects(
    db: AsyncSession = Depends(get_db),
    user = Depends(require_teacher)
):
    """Admin + teacher: lists all subjects."""
    subjects = await subjects_service.list_subjects(db)
    data = [
        SubjectResponse(
            id=s.id,
            name=s.name,
            code=s.code,
            total_marks=s.total_marks
        ).model_dump()
        for s in subjects
    ]
    return success_response(data=data, message="Subjects retrieved")

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_subject(
    payload: SubjectCreate,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin)
):
    """Admin-only: Creates a subject, enforcing unique code."""
    existing = await subjects_service.get_subject_by_code(db, payload.code)
    if existing:
        raise AppException(
            status_code=status.HTTP_409_CONFLICT,
            code="SUBJECT_CODE_EXISTS",
            message=f"Subject with code {payload.code} already exists"
        )

    subject = await subjects_service.create_subject(
        db, payload.name, payload.code, payload.total_marks
    )
    await db.commit()
    await db.refresh(subject)

    data = SubjectResponse(
        id=subject.id,
        name=subject.name,
        code=subject.code,
        total_marks=subject.total_marks
    ).model_dump()
    return success_response(data=data, message="Subject created successfully")

@router.put("/{subject_id}")
async def update_subject(
    subject_id: uuid.UUID,
    payload: SubjectUpdate,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin)
):
    """Admin-only: Updates subject name, code, or total marks."""
    subject = await subjects_service.get_subject_by_id(db, subject_id)
    if not subject:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            code="SUBJECT_NOT_FOUND",
            message="Subject not found"
        )

    if payload.code and payload.code != subject.code:
        existing = await subjects_service.get_subject_by_code(db, payload.code)
        if existing:
            raise AppException(
                status_code=status.HTTP_409_CONFLICT,
                code="SUBJECT_CODE_EXISTS",
                message=f"Subject with code {payload.code} already exists"
            )

    subject = await subjects_service.update_subject(
        db, subject, payload.name, payload.code, payload.total_marks
    )
    await db.commit()
    await db.refresh(subject)

    data = SubjectResponse(
        id=subject.id,
        name=subject.name,
        code=subject.code,
        total_marks=subject.total_marks
    ).model_dump()
    return success_response(data=data, message="Subject updated successfully")

@router.delete("/{subject_id}")
async def delete_subject(
    subject_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin)
):
    """Admin-only: Deletes a subject."""
    subject = await subjects_service.get_subject_by_id(db, subject_id)
    if not subject:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            code="SUBJECT_NOT_FOUND",
            message="Subject not found"
        )

    await subjects_service.delete_subject(db, subject)
    await db.commit()
    return success_response(data={"id": str(subject_id)}, message="Subject deleted")

