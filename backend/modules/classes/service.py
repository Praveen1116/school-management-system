import uuid
from typing import Sequence
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from modules.classes.model import Class, StudentClassEnrollment, ClassSubjectAssignment
from modules.students.model import Student

async def get_class_by_id(db: AsyncSession, class_id: uuid.UUID) -> Class | None:
    """Retrieves class by ID."""
    result = await db.execute(select(Class).where(Class.id == class_id))
    return result.scalar_one_or_none()

async def get_class_by_natural_key(
    db: AsyncSession,
    name: str,
    section: str,
    academic_year: int
) -> Class | None:
    """Finds class matching unique composite key (name, section, academic_year)."""
    query = select(Class).where(
        Class.name == name,
        Class.section == section,
        Class.academic_year == academic_year
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def list_classes(
    db: AsyncSession,
    teacher_id: uuid.UUID | None = None
) -> Sequence[Class]:
    """Lists all classes, or classes assigned to a specific teacher."""
    if teacher_id is not None:
        query = (
            select(Class)
            .join(ClassSubjectAssignment, Class.id == ClassSubjectAssignment.class_id)
            .where(ClassSubjectAssignment.teacher_id == teacher_id)
            .distinct()
            .order_by(Class.name.asc(), Class.section.asc())
        )
    else:
        query = select(Class).order_by(Class.name.asc(), Class.section.asc())

    result = await db.execute(query)
    return result.scalars().all()

async def create_class(
    db: AsyncSession,
    name: str,
    section: str,
    academic_year: int
) -> Class:
    """Creates a new class."""
    new_class = Class(name=name, section=section, academic_year=academic_year)
    db.add(new_class)
    await db.flush()
    return new_class

async def update_class(
    db: AsyncSession,
    class_obj: Class,
    name: str | None = None,
    section: str | None = None,
    academic_year: int | None = None
) -> Class:
    """Updates class properties."""
    if name is not None:
        class_obj.name = name
    if section is not None:
        class_obj.section = section
    if academic_year is not None:
        class_obj.academic_year = academic_year
    await db.flush()
    return class_obj

async def list_class_students(db: AsyncSession, class_id: uuid.UUID) -> list[dict]:
    """Lists all students enrolled in a class."""
    query = (
        select(Student, StudentClassEnrollment.academic_year)
        .join(StudentClassEnrollment, Student.id == StudentClassEnrollment.student_id)
        .where(StudentClassEnrollment.class_id == class_id, Student.is_active.is_(True))
        .order_by(Student.full_name.asc())
    )
    rows = (await db.execute(query)).all()
    return [
        {
            "id": s.id,
            "full_name": s.full_name,
            "roll_number": s.roll_number,
            "date_of_birth": s.date_of_birth,
            "academic_year": yr,
            "is_active": s.is_active
        }
        for s, yr in rows
    ]

async def is_teacher_assigned_to_class(
    db: AsyncSession,
    teacher_id: uuid.UUID,
    class_id: uuid.UUID
) -> bool:
    """Checks whether teacher is assigned to any subject in the given class."""
    query = select(ClassSubjectAssignment.id).where(
        ClassSubjectAssignment.teacher_id == teacher_id,
        ClassSubjectAssignment.class_id == class_id
    ).limit(1)
    result = await db.execute(query)
    return result.scalars().first() is not None

async def is_student_enrolled_in_class(
    db: AsyncSession,
    student_id: uuid.UUID,
    class_id: uuid.UUID,
    academic_year: int | None = None
) -> bool:
    """Checks whether student is enrolled in the given class."""
    query = select(StudentClassEnrollment.id).where(
        StudentClassEnrollment.student_id == student_id,
        StudentClassEnrollment.class_id == class_id
    )
    if academic_year is not None:
        query = query.where(StudentClassEnrollment.academic_year == academic_year)
    query = query.limit(1)
    result = await db.execute(query)
    return result.scalars().first() is not None

async def get_student_class_id(db: AsyncSession, student_id: uuid.UUID) -> uuid.UUID | None:
    """Gets the class_id where the student is currently enrolled."""
    query = (
        select(StudentClassEnrollment.class_id)
        .where(StudentClassEnrollment.student_id == student_id)
        .order_by(StudentClassEnrollment.academic_year.desc())
        .limit(1)
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def is_teacher_assigned_to_student_subject(
    db: AsyncSession,
    teacher_id: uuid.UUID,
    student_id: uuid.UUID,
    subject_id: uuid.UUID
) -> bool:
    """Checks whether teacher teaches the given subject in the class the student is enrolled in."""
    query = (
        select(ClassSubjectAssignment.id)
        .join(
            StudentClassEnrollment,
            ClassSubjectAssignment.class_id == StudentClassEnrollment.class_id
        )
        .where(
            StudentClassEnrollment.student_id == student_id,
            ClassSubjectAssignment.subject_id == subject_id,
            ClassSubjectAssignment.teacher_id == teacher_id
        )
        .limit(1)
    )
    result = await db.execute(query)
    return result.scalars().first() is not None

# Enrollments
async def get_enrollment_by_key(
    db: AsyncSession,
    student_id: uuid.UUID,
    class_id: uuid.UUID,
    academic_year: int
) -> StudentClassEnrollment | None:
    query = select(StudentClassEnrollment).where(
        StudentClassEnrollment.student_id == student_id,
        StudentClassEnrollment.class_id == class_id,
        StudentClassEnrollment.academic_year == academic_year
    )
    return (await db.execute(query)).scalar_one_or_none()

async def get_enrollment_by_id(db: AsyncSession, enrollment_id: uuid.UUID) -> StudentClassEnrollment | None:
    result = await db.execute(select(StudentClassEnrollment).where(StudentClassEnrollment.id == enrollment_id))
    return result.scalar_one_or_none()

async def create_enrollment(
    db: AsyncSession,
    student_id: uuid.UUID,
    class_id: uuid.UUID,
    academic_year: int
) -> StudentClassEnrollment:
    enrollment = StudentClassEnrollment(
        student_id=student_id,
        class_id=class_id,
        academic_year=academic_year
    )
    db.add(enrollment)
    await db.flush()
    return enrollment

async def delete_enrollment(db: AsyncSession, enrollment: StudentClassEnrollment) -> None:
    await db.delete(enrollment)
    await db.flush()

# Assignments
async def get_assignment_by_key(
    db: AsyncSession,
    class_id: uuid.UUID,
    subject_id: uuid.UUID,
    academic_year: int
) -> ClassSubjectAssignment | None:
    query = select(ClassSubjectAssignment).where(
        ClassSubjectAssignment.class_id == class_id,
        ClassSubjectAssignment.subject_id == subject_id,
        ClassSubjectAssignment.academic_year == academic_year
    )
    return (await db.execute(query)).scalar_one_or_none()

async def get_assignment_by_id(db: AsyncSession, assignment_id: uuid.UUID) -> ClassSubjectAssignment | None:
    result = await db.execute(select(ClassSubjectAssignment).where(ClassSubjectAssignment.id == assignment_id))
    return result.scalar_one_or_none()

async def list_assignments(db: AsyncSession) -> Sequence[ClassSubjectAssignment]:
    query = select(ClassSubjectAssignment).order_by(ClassSubjectAssignment.academic_year.desc())
    return (await db.execute(query)).scalars().all()

async def create_assignment(
    db: AsyncSession,
    class_id: uuid.UUID,
    subject_id: uuid.UUID,
    teacher_id: uuid.UUID,
    academic_year: int
) -> ClassSubjectAssignment:
    assignment = ClassSubjectAssignment(
        class_id=class_id,
        subject_id=subject_id,
        teacher_id=teacher_id,
        academic_year=academic_year
    )
    db.add(assignment)
    await db.flush()
    return assignment

async def update_assignment(
    db: AsyncSession,
    assignment: ClassSubjectAssignment,
    teacher_id: uuid.UUID | None = None,
    academic_year: int | None = None
) -> ClassSubjectAssignment:
    if teacher_id is not None:
        assignment.teacher_id = teacher_id
    if academic_year is not None:
        assignment.academic_year = academic_year
    await db.flush()
    return assignment

async def delete_assignment(db: AsyncSession, assignment: ClassSubjectAssignment) -> None:
    await db.delete(assignment)
    await db.flush()

