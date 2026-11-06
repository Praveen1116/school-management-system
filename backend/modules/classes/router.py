import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies import (
    get_db,
    get_current_user,
    require_admin,
    require_teacher,
    success_response,
    AppException
)
from modules.classes.schemas import (
    ClassCreate,
    ClassUpdate,
    ClassResponse,
    EnrollmentCreate,
    EnrollmentResponse,
    AssignmentCreate,
    AssignmentUpdate,
    AssignmentResponse
)
from modules.classes import service as classes_service
from modules.teachers import service as teachers_service
from modules.students import service as students_service

router = APIRouter()
enrollments_router = APIRouter()
assignments_router = APIRouter()

# --- Classes Endpoints ---

@router.get("")
async def list_classes(
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    """Admin sees all classes; Teacher sees only assigned classes."""
    if user.role == "admin":
        classes = await classes_service.list_classes(db)
    elif user.role == "teacher":
        teacher = await teachers_service.get_teacher_by_user_id(db, user.id)
        if not teacher:
            return success_response(data=[], message="No classes found")
        classes = await classes_service.list_classes(db, teacher_id=teacher.id)
    else:
        raise AppException(
            status_code=status.HTTP_403_FORBIDDEN,
            code="FORBIDDEN_ACCESS",
            message="Not authorized to list classes"
        )

    data = [
        ClassResponse(
            id=c.id,
            name=c.name,
            section=c.section,
            academic_year=c.academic_year
        ).model_dump()
        for c in classes
    ]
    return success_response(data=data, message="Classes retrieved")

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_class(
    payload: ClassCreate,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin)
):
    """Admin-only: Creates a class, enforcing UniqueConstraint on (name, section, academic_year)."""
    existing = await classes_service.get_class_by_natural_key(
        db, payload.name, payload.section, payload.academic_year
    )
    if existing:
        raise AppException(
            status_code=status.HTTP_409_CONFLICT,
            code="CLASS_EXISTS",
            message=f"Class {payload.name}-{payload.section} ({payload.academic_year}) already exists"
        )

    class_obj = await classes_service.create_class(
        db, payload.name, payload.section, payload.academic_year
    )
    await db.commit()
    await db.refresh(class_obj)

    data = ClassResponse(
        id=class_obj.id,
        name=class_obj.name,
        section=class_obj.section,
        academic_year=class_obj.academic_year
    ).model_dump()
    return success_response(data=data, message="Class created successfully")

@router.get("/{class_id}")
async def get_class(
    class_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    """Admin + teacher (if assigned)."""
    class_obj = await classes_service.get_class_by_id(db, class_id)
    if not class_obj:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            code="CLASS_NOT_FOUND",
            message="Class not found"
        )

    if user.role == "teacher":
        teacher = await teachers_service.get_teacher_by_user_id(db, user.id)
        if not teacher or not await classes_service.is_teacher_assigned_to_class(db, teacher.id, class_id):
            raise AppException(
                status_code=status.HTTP_403_FORBIDDEN,
                code="TEACHER_NOT_ASSIGNED",
                message="You are not assigned to this class"
            )
    elif user.role != "admin":
        raise AppException(
            status_code=status.HTTP_403_FORBIDDEN,
            code="FORBIDDEN_ACCESS",
            message="Not authorized"
        )

    data = ClassResponse(
        id=class_obj.id,
        name=class_obj.name,
        section=class_obj.section,
        academic_year=class_obj.academic_year
    ).model_dump()
    return success_response(data=data, message="Class retrieved")

@router.put("/{class_id}")
async def update_class(
    class_id: uuid.UUID,
    payload: ClassUpdate,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin)
):
    """Admin-only: updates class name, section, or academic year."""
    class_obj = await classes_service.get_class_by_id(db, class_id)
    if not class_obj:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            code="CLASS_NOT_FOUND",
            message="Class not found"
        )

    name = payload.name or class_obj.name
    section = payload.section or class_obj.section
    year = payload.academic_year or class_obj.academic_year

    existing = await classes_service.get_class_by_natural_key(db, name, section, year)
    if existing and existing.id != class_id:
        raise AppException(
            status_code=status.HTTP_409_CONFLICT,
            code="CLASS_EXISTS",
            message=f"Class {name}-{section} ({year}) already exists"
        )

    class_obj = await classes_service.update_class(
        db, class_obj, payload.name, payload.section, payload.academic_year
    )
    await db.commit()
    await db.refresh(class_obj)

    data = ClassResponse(
        id=class_obj.id,
        name=class_obj.name,
        section=class_obj.section,
        academic_year=class_obj.academic_year
    ).model_dump()
    return success_response(data=data, message="Class updated successfully")

@router.get("/{class_id}/students")
async def get_class_students(
    class_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    """Admin + teacher (if assigned): lists enrolled students."""
    class_obj = await classes_service.get_class_by_id(db, class_id)
    if not class_obj:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            code="CLASS_NOT_FOUND",
            message="Class not found"
        )

    if user.role == "teacher":
        teacher = await teachers_service.get_teacher_by_user_id(db, user.id)
        if not teacher or not await classes_service.is_teacher_assigned_to_class(db, teacher.id, class_id):
            raise AppException(
                status_code=status.HTTP_403_FORBIDDEN,
                code="TEACHER_NOT_ASSIGNED",
                message="You are not assigned to this class"
            )
    elif user.role != "admin":
        raise AppException(
            status_code=status.HTTP_403_FORBIDDEN,
            code="FORBIDDEN_ACCESS",
            message="Not authorized"
        )

    students = await classes_service.list_class_students(db, class_id)
    return success_response(data=students, message="Class students retrieved")


# --- Enrollments Endpoints ---

@router.post("/enrollments", status_code=status.HTTP_201_CREATED)
@enrollments_router.post("", status_code=status.HTTP_201_CREATED)
async def create_enrollment(
    payload: EnrollmentCreate,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin)
):
    """Admin-only: Enroll a student into a class for an academic year."""
    existing = await classes_service.get_enrollment_by_key(
        db, payload.student_id, payload.class_id, payload.academic_year
    )
    if existing:
        raise AppException(
            status_code=status.HTTP_409_CONFLICT,
            code="STUDENT_ALREADY_ENROLLED",
            message="Student already enrolled in this class for this academic year"
        )

    enrollment = await classes_service.create_enrollment(
        db, payload.student_id, payload.class_id, payload.academic_year
    )
    await db.commit()
    await db.refresh(enrollment)

    data = EnrollmentResponse(
        id=enrollment.id,
        student_id=enrollment.student_id,
        class_id=enrollment.class_id,
        academic_year=enrollment.academic_year
    ).model_dump()
    return success_response(data=data, message="Student enrolled successfully")

@router.delete("/enrollments/{enrollment_id}")
@enrollments_router.delete("/{enrollment_id}")
async def delete_enrollment(
    enrollment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin)
):
    """Admin-only: Remove an enrollment."""
    enrollment = await classes_service.get_enrollment_by_id(db, enrollment_id)
    if not enrollment:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            code="ENROLLMENT_NOT_FOUND",
            message="Enrollment not found"
        )

    await classes_service.delete_enrollment(db, enrollment)
    await db.commit()
    return success_response(data={"id": str(enrollment_id)}, message="Enrollment removed")


# --- Assignments Endpoints ---

@router.get("/assignments")
@assignments_router.get("")
async def list_assignments(
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin)
):
    """Admin-only: List all class-subject-teacher assignments."""
    assignments = await classes_service.list_assignments(db)
    data = [
        AssignmentResponse(
            id=a.id,
            class_id=a.class_id,
            subject_id=a.subject_id,
            teacher_id=a.teacher_id,
            academic_year=a.academic_year
        ).model_dump()
        for a in assignments
    ]
    return success_response(data=data, message="Assignments retrieved")

@router.post("/assignments", status_code=status.HTTP_201_CREATED)
@assignments_router.post("", status_code=status.HTTP_201_CREATED)
async def create_assignment(
    payload: AssignmentCreate,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin)
):
    """Admin-only: Assign a subject and teacher to a class."""
    existing = await classes_service.get_assignment_by_key(
        db, payload.class_id, payload.subject_id, payload.academic_year
    )
    if existing:
        raise AppException(
            status_code=status.HTTP_409_CONFLICT,
            code="SUBJECT_ALREADY_ASSIGNED",
            message="Subject already assigned to this class for this academic year"
        )

    assignment = await classes_service.create_assignment(
        db, payload.class_id, payload.subject_id, payload.teacher_id, payload.academic_year
    )
    await db.commit()
    await db.refresh(assignment)

    data = AssignmentResponse(
        id=assignment.id,
        class_id=assignment.class_id,
        subject_id=assignment.subject_id,
        teacher_id=assignment.teacher_id,
        academic_year=assignment.academic_year
    ).model_dump()
    return success_response(data=data, message="Subject assigned successfully")

@router.put("/assignments/{assignment_id}")
@assignments_router.put("/{assignment_id}")
async def update_assignment(
    assignment_id: uuid.UUID,
    payload: AssignmentUpdate,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin)
):
    """Admin-only: Update teacher or academic year for an assignment."""
    assignment = await classes_service.get_assignment_by_id(db, assignment_id)
    if not assignment:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            code="ASSIGNMENT_NOT_FOUND",
            message="Assignment not found"
        )

    assignment = await classes_service.update_assignment(
        db, assignment, teacher_id=payload.teacher_id, academic_year=payload.academic_year
    )
    await db.commit()
    await db.refresh(assignment)

    data = AssignmentResponse(
        id=assignment.id,
        class_id=assignment.class_id,
        subject_id=assignment.subject_id,
        teacher_id=assignment.teacher_id,
        academic_year=assignment.academic_year
    ).model_dump()
    return success_response(data=data, message="Assignment updated successfully")

@router.delete("/assignments/{assignment_id}")
@assignments_router.delete("/{assignment_id}")
async def delete_assignment(
    assignment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin)
):
    """Admin-only: Remove a class-subject-teacher assignment."""
    assignment = await classes_service.get_assignment_by_id(db, assignment_id)
    if not assignment:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            code="ASSIGNMENT_NOT_FOUND",
            message="Assignment not found"
        )

    await classes_service.delete_assignment(db, assignment)
    await db.commit()
    return success_response(data={"id": str(assignment_id)}, message="Assignment removed")

