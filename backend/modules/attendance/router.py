import uuid
from datetime import date
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies import (
    get_db,
    get_current_user,
    require_teacher,
    success_response,
    AppException
)
from modules.attendance.schemas import AttendanceCreate, AttendanceUpdate, AttendanceResponse
from modules.attendance import service as attendance_service
from modules.classes import service as classes_service
from modules.teachers import service as teachers_service
from modules.teachers.model import Teacher
from modules.students import service as students_service
from modules.audit import service as audit_service

router = APIRouter()

@router.post("", status_code=status.HTTP_201_CREATED)
async def record_attendance(
    payload: AttendanceCreate,
    db: AsyncSession = Depends(get_db),
    user = Depends(require_teacher)
):
    """Records daily attendance. Enforces class assignment, enrollment, and uniqueness."""
    # 1. If teacher, verify assigned to class
    teacher_record = None
    if user.role == "teacher":
        teacher_record = await teachers_service.get_teacher_by_user_id(db, user.id)
        if not teacher_record or not await classes_service.is_teacher_assigned_to_class(db, teacher_record.id, payload.class_id):
            raise AppException(
                status_code=status.HTTP_403_FORBIDDEN,
                code="TEACHER_NOT_ASSIGNED",
                message="Teacher is not assigned to this class"
            )
        recorded_by = teacher_record.id
    else:
        # Admin can record attendance for any class. Use an assigned teacher or fallback teacher for FK
        t_res = await db.execute(select(Teacher).where(Teacher.is_active.is_(True)).limit(1))
        t = t_res.scalar_one_or_none()
        if not t:
            raise AppException(
                status_code=status.HTTP_400_BAD_REQUEST,
                code="NO_TEACHERS_FOUND",
                message="Cannot record attendance: no teacher records exist"
            )
        recorded_by = t.id

    # 2. Verify student is enrolled in the class
    is_enrolled = await classes_service.is_student_enrolled_in_class(db, payload.student_id, payload.class_id)
    if not is_enrolled:
        raise AppException(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="STUDENT_NOT_IN_CLASS",
            message="Student is not enrolled in this class"
        )

    # 3. Check UniqueConstraint (student_id, attendance_date, session)
    existing = await attendance_service.get_duplicate_record(
        db, payload.student_id, payload.attendance_date, payload.session
    )
    if existing:
        raise AppException(
            status_code=status.HTTP_409_CONFLICT,
            code="DUPLICATE_ATTENDANCE",
            message="Attendance already recorded for this student on this date and session"
        )

    # 4. Create record
    record = await attendance_service.create_attendance_record(
        db=db,
        student_id=payload.student_id,
        class_id=payload.class_id,
        recorded_by=recorded_by,
        attendance_date=payload.attendance_date,
        session=payload.session,
        status=payload.status
    )

    # 5. Write to audit_log
    await audit_service.log_action(
        db=db,
        actor_id=user.id,
        action=audit_service.ATTENDANCE_RECORDED,
        entity_type="attendance",
        entity_id=record.id,
        new_value={
            "student_id": str(record.student_id),
            "date": str(record.attendance_date),
            "session": record.session,
            "status": record.status
        }
    )
    await db.commit()
    await db.refresh(record)

    data = AttendanceResponse(
        id=record.id,
        student_id=record.student_id,
        class_id=record.class_id,
        recorded_by=record.recorded_by,
        attendance_date=record.attendance_date,
        session=record.session,
        status=record.status,
        created_at=record.created_at
    ).model_dump()
    return success_response(data=data, message="Attendance recorded successfully")

@router.put("/{record_id}")
async def update_attendance(
    record_id: uuid.UUID,
    payload: AttendanceUpdate,
    db: AsyncSession = Depends(get_db),
    user = Depends(require_teacher)
):
    """Allows updating attendance status (e.g. absent -> present). Requires class assignment."""
    record = await attendance_service.get_attendance_by_id(db, record_id)
    if not record:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            code="ATTENDANCE_NOT_FOUND",
            message="Attendance record not found"
        )

    if user.role == "teacher":
        teacher = await teachers_service.get_teacher_by_user_id(db, user.id)
        if not teacher or not await classes_service.is_teacher_assigned_to_class(db, teacher.id, record.class_id):
            raise AppException(
                status_code=status.HTTP_403_FORBIDDEN,
                code="TEACHER_NOT_ASSIGNED",
                message="You are not assigned to this class"
            )

    old_status = record.status
    record = await attendance_service.update_attendance_status(db, record, payload.status)

    await audit_service.log_action(
        db=db,
        actor_id=user.id,
        action=audit_service.ATTENDANCE_UPDATED,
        entity_type="attendance",
        entity_id=record.id,
        old_value={"status": old_status},
        new_value={"status": record.status}
    )
    await db.commit()
    await db.refresh(record)

    data = AttendanceResponse(
        id=record.id,
        student_id=record.student_id,
        class_id=record.class_id,
        recorded_by=record.recorded_by,
        attendance_date=record.attendance_date,
        session=record.session,
        status=record.status,
        created_at=record.created_at
    ).model_dump()
    return success_response(data=data, message="Attendance updated successfully")

@router.get("/class/{class_id}")
async def get_class_attendance_records(
    class_id: uuid.UUID,
    date_from: date = Query(...),
    date_to: date = Query(...),
    db: AsyncSession = Depends(get_db),
    user = Depends(require_teacher)
):
    """Admin + teacher (assigned only): returns class attendance records and summary."""
    if user.role == "teacher":
        teacher = await teachers_service.get_teacher_by_user_id(db, user.id)
        if not teacher or not await classes_service.is_teacher_assigned_to_class(db, teacher.id, class_id):
            raise AppException(
                status_code=status.HTTP_403_FORBIDDEN,
                code="TEACHER_NOT_ASSIGNED",
                message="You are not assigned to this class"
            )

    records, summary = await attendance_service.get_class_attendance(db, class_id, date_from, date_to)
    return success_response(
        data={"records": records, "summary": summary},
        message="Class attendance retrieved"
    )

@router.get("/student/{student_id}")
async def get_student_attendance_records(
    student_id: uuid.UUID,
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    """Admin + assigned teacher + student's guardian."""
    student = await students_service.get_student_by_id(db, student_id)
    if not student:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            code="STUDENT_NOT_FOUND",
            message="Student not found"
        )

    # Check access permissions
    if user.role == "admin":
        pass
    elif user.role == "guardian":
        if student.guardian_id != user.id:
            raise AppException(
                status_code=status.HTTP_403_FORBIDDEN,
                code="NOT_YOUR_STUDENT",
                message="You can only view attendance for your own students"
            )
    elif user.role == "teacher":
        teacher = await teachers_service.get_teacher_by_user_id(db, user.id)
        student_class_id = await classes_service.get_student_class_id(db, student.id)
        if not teacher or not student_class_id or not await classes_service.is_teacher_assigned_to_class(db, teacher.id, student_class_id):
            raise AppException(
                status_code=status.HTTP_403_FORBIDDEN,
                code="TEACHER_NOT_ASSIGNED",
                message="You are not assigned to this student's class"
            )
    else:
        raise AppException(
            status_code=status.HTTP_403_FORBIDDEN,
            code="FORBIDDEN_ACCESS",
            message="Not authorized"
        )

    records, summary = await attendance_service.get_student_attendance(db, student_id, date_from, date_to)
    return success_response(
        data={"records": records, "summary": summary},
        message="Student attendance retrieved"
    )

