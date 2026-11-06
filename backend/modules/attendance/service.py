import uuid
from typing import Sequence
from datetime import date
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from modules.attendance.model import AttendanceRecord
from modules.students.model import Student
from modules.classes.model import StudentClassEnrollment

async def get_attendance_by_id(db: AsyncSession, record_id: uuid.UUID) -> AttendanceRecord | None:
    result = await db.execute(select(AttendanceRecord).where(AttendanceRecord.id == record_id))
    return result.scalar_one_or_none()

async def get_duplicate_record(
    db: AsyncSession,
    student_id: uuid.UUID,
    attendance_date: date,
    session: str
) -> AttendanceRecord | None:
    query = select(AttendanceRecord).where(
        AttendanceRecord.student_id == student_id,
        AttendanceRecord.attendance_date == attendance_date,
        AttendanceRecord.session == session
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def create_attendance_record(
    db: AsyncSession,
    student_id: uuid.UUID,
    class_id: uuid.UUID,
    recorded_by: uuid.UUID,
    attendance_date: date,
    session: str,
    status: str
) -> AttendanceRecord:
    record = AttendanceRecord(
        student_id=student_id,
        class_id=class_id,
        recorded_by=recorded_by,
        attendance_date=attendance_date,
        session=session,
        status=status
    )
    db.add(record)
    await db.flush()
    return record

async def update_attendance_status(
    db: AsyncSession,
    record: AttendanceRecord,
    new_status: str
) -> AttendanceRecord:
    record.status = new_status
    await db.flush()
    return record

async def get_class_attendance(
    db: AsyncSession,
    class_id: uuid.UUID,
    date_from: date,
    date_to: date
) -> tuple[list[dict], dict]:
    """Returns attendance records for a class between dates with student names and summary."""
    query = (
        select(AttendanceRecord, Student.full_name, Student.roll_number)
        .join(Student, AttendanceRecord.student_id == Student.id)
        .where(
            AttendanceRecord.class_id == class_id,
            AttendanceRecord.attendance_date >= date_from,
            AttendanceRecord.attendance_date <= date_to
        )
        .order_by(AttendanceRecord.attendance_date.desc(), Student.roll_number.asc())
    )
    rows = (await db.execute(query)).all()

    # Count distinct enrolled students in class
    enrolled_count_query = (
        select(func.count(StudentClassEnrollment.id))
        .where(StudentClassEnrollment.class_id == class_id)
    )
    total_students = (await db.execute(enrolled_count_query)).scalar_one()

    records = []
    present_count = 0
    absent_count = 0
    late_count = 0

    for rec, full_name, roll_number in rows:
        if rec.status == "present":
            present_count += 1
        elif rec.status == "absent":
            absent_count += 1
        elif rec.status == "late":
            late_count += 1

        records.append({
            "id": rec.id,
            "student_id": rec.student_id,
            "student_name": full_name,
            "roll_number": roll_number,
            "class_id": rec.class_id,
            "recorded_by": rec.recorded_by,
            "attendance_date": rec.attendance_date,
            "session": rec.session,
            "status": rec.status,
            "created_at": rec.created_at
        })

    summary = {
        "total_students": total_students,
        "total_records": len(records),
        "present_count": present_count,
        "absent_count": absent_count,
        "late_count": late_count
    }
    return records, summary

async def get_student_attendance(
    db: AsyncSession,
    student_id: uuid.UUID,
    date_from: date | None = None,
    date_to: date | None = None
) -> tuple[list[dict], dict]:
    """Returns attendance records for a student with summary and attendance percentage."""
    query = select(AttendanceRecord).where(AttendanceRecord.student_id == student_id)
    if date_from:
        query = query.where(AttendanceRecord.attendance_date >= date_from)
    if date_to:
        query = query.where(AttendanceRecord.attendance_date <= date_to)

    query = query.order_by(AttendanceRecord.attendance_date.desc())
    records_obj = (await db.execute(query)).scalars().all()

    total_days = len(records_obj)
    present_count = sum(1 for r in records_obj if r.status == "present")
    absent_count = sum(1 for r in records_obj if r.status == "absent")
    late_count = sum(1 for r in records_obj if r.status == "late")

    # Percentage: (present / total_days) * 100, late can count or present can be raw
    percentage = round((present_count / total_days * 100), 1) if total_days > 0 else 0.0

    records = [
        {
            "id": r.id,
            "student_id": r.student_id,
            "class_id": r.class_id,
            "recorded_by": r.recorded_by,
            "attendance_date": r.attendance_date,
            "session": r.session,
            "status": r.status,
            "created_at": r.created_at
        }
        for r in records_obj
    ]

    summary = {
        "total_days": total_days,
        "present_count": present_count,
        "absent_count": absent_count,
        "late_count": late_count,
        "percentage": percentage
    }
    return records, summary

