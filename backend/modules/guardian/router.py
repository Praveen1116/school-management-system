import uuid
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies import get_db, require_guardian, success_response
from modules.guardian.schemas import GuardianStudentResponse
from modules.guardian import service as guardian_service

router = APIRouter()

@router.get("/me/students")
async def get_my_students(
    db: AsyncSession = Depends(get_db),
    user = Depends(require_guardian)
):
    """Returns all students belonging to the authenticated guardian."""
    students = await guardian_service.get_my_students(db, user.id)
    data = [
        GuardianStudentResponse(
            id=s.id,
            guardian_id=s.guardian_id,
            full_name=s.full_name,
            roll_number=s.roll_number,
            date_of_birth=s.date_of_birth,
            is_active=s.is_active
        ).model_dump()
        for s in students
    ]
    return success_response(data=data, message="Guardian students retrieved")

@router.get("/me/students/{student_id}/attendance")
async def get_my_student_attendance(
    student_id: uuid.UUID,
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    db: AsyncSession = Depends(get_db),
    user = Depends(require_guardian)
):
    """Returns attendance and summary for guardian's own student."""
    if user.role != "admin":
        await guardian_service.verify_student_ownership(db, student_id, user.id)

    records, summary = await guardian_service.get_guardian_student_attendance(
        db, student_id, date_from, date_to
    )
    return success_response(
        data={"records": records, "summary": summary},
        message="Student attendance retrieved"
    )

@router.get("/me/students/{student_id}/report-card")
async def get_my_student_report_card(
    student_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user = Depends(require_guardian)
):
    """Returns academic report card for guardian's own student."""
    if user.role != "admin":
        await guardian_service.verify_student_ownership(db, student_id, user.id)

    report_card = await guardian_service.get_guardian_student_report_card(db, student_id)
    return success_response(data=report_card, message="Student report card retrieved")

@router.get("/me/students/{student_id}/fee-summary")
async def get_my_student_fee_summary(
    student_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user = Depends(require_guardian)
):
    """Returns fee invoices and dynamic balance for guardian's own student."""
    if user.role != "admin":
        await guardian_service.verify_student_ownership(db, student_id, user.id)

    fee_summary = await guardian_service.get_guardian_student_fees(db, student_id)
    return success_response(data=fee_summary, message="Student fee summary retrieved")

