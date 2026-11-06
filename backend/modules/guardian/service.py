import uuid
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status
from dependencies import AppException
from modules.students import service as students_service
from modules.attendance import service as attendance_service
from modules.fees import service as fees_service

async def get_my_students(db: AsyncSession, guardian_id: uuid.UUID):
    return await students_service.get_students_by_guardian_id(db, guardian_id)

async def verify_student_ownership(db: AsyncSession, student_id: uuid.UUID, guardian_id: uuid.UUID):
    student = await students_service.get_student_by_id(db, student_id)
    if not student:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            code="STUDENT_NOT_FOUND",
            message="Student not found"
        )
    if student.guardian_id != guardian_id:
        raise AppException(
            status_code=status.HTTP_403_FORBIDDEN,
            code="NOT_YOUR_STUDENT",
            message="You can only access records for your own students"
        )
    return student

async def get_guardian_student_attendance(
    db: AsyncSession,
    student_id: uuid.UUID,
    date_from: date | None = None,
    date_to: date | None = None
):
    return await attendance_service.get_student_attendance(db, student_id, date_from, date_to)

async def get_guardian_student_report_card(db: AsyncSession, student_id: uuid.UUID):
    return await students_service.get_student_report_card(db, student_id)

async def get_guardian_student_fees(db: AsyncSession, student_id: uuid.UUID):
    return await fees_service.get_student_fee_summary(db, student_id)

