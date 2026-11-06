import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies import (
    get_db,
    get_current_user,
    require_admin,
    success_response,
    paginated_response,
    AppException
)
from modules.students.schemas import StudentCreate, StudentUpdate, StudentResponse
from modules.students import service as students_service
from modules.classes import service as classes_service
from modules.teachers import service as teachers_service
from modules.audit import service as audit_service

router = APIRouter()

async def verify_student_access(user, student, db: AsyncSession):
    """Enforces access control: admin OR student's guardian OR assigned teacher."""
    if user.role == "admin":
        return
    if user.role == "guardian" and student.guardian_id == user.id:
        return
    if user.role == "teacher":
        teacher = await teachers_service.get_teacher_by_user_id(db, user.id)
        if teacher:
            student_class_id = await classes_service.get_student_class_id(db, student.id)
            if student_class_id and await classes_service.is_teacher_assigned_to_class(db, teacher.id, student_class_id):
                return
    raise AppException(
        status_code=status.HTTP_403_FORBIDDEN,
        code="FORBIDDEN_ACCESS",
        message="You are not authorized to view this student's records"
    )

@router.get("")
async def list_students(
    search: str | None = Query(None),
    class_id: uuid.UUID | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin)
):
    """Admin-only: Searches students with filtering and pagination."""
    students, total = await students_service.list_students(
        db, search=search, class_id=class_id, page=page, limit=limit
    )
    data = [
        StudentResponse(
            id=s.id,
            guardian_id=s.guardian_id,
            full_name=s.full_name,
            roll_number=s.roll_number,
            date_of_birth=s.date_of_birth,
            is_active=s.is_active,
            created_at=s.created_at
        ).model_dump()
        for s in students
    ]
    return paginated_response(data=data, page=page, limit=limit, total=total)

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_student(
    payload: StudentCreate,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin)
):
    """Admin-only: Creates a student, enforcing unique roll number."""
    existing = await students_service.get_student_by_roll_number(db, payload.roll_number)
    if existing:
        raise AppException(
            status_code=status.HTTP_409_CONFLICT,
            code="ROLL_NUMBER_EXISTS",
            message=f"Student with roll number {payload.roll_number} already exists"
        )

    student = await students_service.create_student(
        db=db,
        guardian_id=payload.guardian_id,
        full_name=payload.full_name,
        roll_number=payload.roll_number,
        date_of_birth=payload.date_of_birth
    )

    await audit_service.log_action(
        db=db,
        actor_id=admin.id,
        action=audit_service.STUDENT_CREATED,
        entity_type="student",
        entity_id=student.id,
        new_value={"roll_number": student.roll_number, "full_name": student.full_name}
    )
    await db.commit()
    await db.refresh(student)

    data = StudentResponse(
        id=student.id,
        guardian_id=student.guardian_id,
        full_name=student.full_name,
        roll_number=student.roll_number,
        date_of_birth=student.date_of_birth,
        is_active=student.is_active,
        created_at=student.created_at
    ).model_dump()
    return success_response(data=data, message="Student created successfully")

@router.get("/{student_id}")
async def get_student(
    student_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    """Admin + teacher (assigned to student's class) + student's guardian."""
    student = await students_service.get_student_by_id(db, student_id)
    if not student:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            code="STUDENT_NOT_FOUND",
            message="Student not found"
        )

    await verify_student_access(user, student, db)

    data = StudentResponse(
        id=student.id,
        guardian_id=student.guardian_id,
        full_name=student.full_name,
        roll_number=student.roll_number,
        date_of_birth=student.date_of_birth,
        is_active=student.is_active,
        created_at=student.created_at
    ).model_dump()
    return success_response(data=data, message="Student retrieved")

@router.put("/{student_id}")
async def update_student(
    student_id: uuid.UUID,
    payload: StudentUpdate,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin)
):
    """Admin-only: Updates student details, enforcing unique roll number."""
    student = await students_service.get_student_by_id(db, student_id)
    if not student:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            code="STUDENT_NOT_FOUND",
            message="Student not found"
        )

    if payload.roll_number and payload.roll_number != student.roll_number:
        existing = await students_service.get_student_by_roll_number(db, payload.roll_number)
        if existing:
            raise AppException(
                status_code=status.HTTP_409_CONFLICT,
                code="ROLL_NUMBER_EXISTS",
                message=f"Student with roll number {payload.roll_number} already exists"
            )

    old_val = {"full_name": student.full_name, "roll_number": student.roll_number}
    student = await students_service.update_student(
        db, student,
        guardian_id=payload.guardian_id,
        full_name=payload.full_name,
        roll_number=payload.roll_number,
        date_of_birth=payload.date_of_birth
    )
    new_val = {"full_name": student.full_name, "roll_number": student.roll_number}

    await audit_service.log_action(
        db=db,
        actor_id=admin.id,
        action=audit_service.STUDENT_UPDATED,
        entity_type="student",
        entity_id=student.id,
        old_value=old_val,
        new_value=new_val
    )
    await db.commit()
    await db.refresh(student)

    data = StudentResponse(
        id=student.id,
        guardian_id=student.guardian_id,
        full_name=student.full_name,
        roll_number=student.roll_number,
        date_of_birth=student.date_of_birth,
        is_active=student.is_active,
        created_at=student.created_at
    ).model_dump()
    return success_response(data=data, message="Student updated successfully")

@router.delete("/{student_id}")
async def delete_student(
    student_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin)
):
    """Admin-only: Soft deletes a student (is_active=False)."""
    student = await students_service.get_student_by_id(db, student_id)
    if not student:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            code="STUDENT_NOT_FOUND",
            message="Student not found"
        )

    student = await students_service.soft_delete_student(db, student)

    await audit_service.log_action(
        db=db,
        actor_id=admin.id,
        action=audit_service.STUDENT_DEACTIVATED,
        entity_type="student",
        entity_id=student.id,
        old_value={"is_active": True},
        new_value={"is_active": False}
    )
    await db.commit()

    return success_response(
        data={"id": str(student.id), "is_active": student.is_active},
        message="Student deactivated"
    )

@router.get("/{student_id}/report-card")
async def get_student_report_card(
    student_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    """Admin + student's guardian + assigned teacher: gets full academic report card."""
    student = await students_service.get_student_by_id(db, student_id)
    if not student:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            code="STUDENT_NOT_FOUND",
            message="Student not found"
        )

    await verify_student_access(user, student, db)

    report_card = await students_service.get_student_report_card(db, student_id)
    return success_response(
        data={
            "student_id": student.id,
            "full_name": student.full_name,
            "roll_number": student.roll_number,
            "report_card": report_card
        },
        message="Report card retrieved"
    )

