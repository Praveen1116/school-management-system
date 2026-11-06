import uuid
from typing import Sequence
from datetime import date
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from modules.students.model import Student
from modules.classes.model import StudentClassEnrollment
from modules.exams.model import ExamResult, Exam
from modules.subjects.model import Subject

async def get_student_by_id(db: AsyncSession, student_id: uuid.UUID) -> Student | None:
    """Retrieves student by ID."""
    result = await db.execute(select(Student).where(Student.id == student_id))
    return result.scalar_one_or_none()

async def get_student_by_roll_number(db: AsyncSession, roll_number: str) -> Student | None:
    """Retrieves student by unique roll number."""
    result = await db.execute(select(Student).where(Student.roll_number == roll_number))
    return result.scalar_one_or_none()

async def list_students(
    db: AsyncSession,
    search: str | None = None,
    class_id: uuid.UUID | None = None,
    page: int = 1,
    limit: int = 20
) -> tuple[Sequence[Student], int]:
    """Admin-only search by name/roll_number and filter by class_id with pagination."""
    query = select(Student).where(Student.is_active.is_(True))
    count_query = select(func.count(Student.id)).where(Student.is_active.is_(True))

    if class_id is not None:
        query = query.join(StudentClassEnrollment, Student.id == StudentClassEnrollment.student_id).where(
            StudentClassEnrollment.class_id == class_id
        )
        count_query = count_query.join(StudentClassEnrollment, Student.id == StudentClassEnrollment.student_id).where(
            StudentClassEnrollment.class_id == class_id
        )

    if search:
        search_pattern = f"%{search}%"
        filter_expr = (Student.full_name.ilike(search_pattern)) | (Student.roll_number.ilike(search_pattern))
        query = query.where(filter_expr)
        count_query = count_query.where(filter_expr)

    total = (await db.execute(count_query)).scalar_one()

    offset = (page - 1) * limit
    query = query.order_by(Student.roll_number.asc()).offset(offset).limit(limit)
    result = await db.execute(query)
    students = result.scalars().all()
    return students, total

async def create_student(
    db: AsyncSession,
    guardian_id: uuid.UUID,
    full_name: str,
    roll_number: str,
    date_of_birth: date
) -> Student:
    """Creates a new student record."""
    student = Student(
        guardian_id=guardian_id,
        full_name=full_name,
        roll_number=roll_number,
        date_of_birth=date_of_birth,
        is_active=True
    )
    db.add(student)
    await db.flush()
    return student

async def update_student(
    db: AsyncSession,
    student: Student,
    guardian_id: uuid.UUID | None = None,
    full_name: str | None = None,
    roll_number: str | None = None,
    date_of_birth: date | None = None
) -> Student:
    """Updates student fields."""
    if guardian_id is not None:
        student.guardian_id = guardian_id
    if full_name is not None:
        student.full_name = full_name
    if roll_number is not None:
        student.roll_number = roll_number
    if date_of_birth is not None:
        student.date_of_birth = date_of_birth
    await db.flush()
    return student

async def soft_delete_student(db: AsyncSession, student: Student) -> Student:
    """Soft deletes student by setting is_active=False."""
    student.is_active = False
    await db.flush()
    return student

async def get_students_by_guardian_id(
    db: AsyncSession,
    guardian_id: uuid.UUID
) -> Sequence[Student]:
    """Finds all active students for a given guardian user ID."""
    query = select(Student).where(
        Student.guardian_id == guardian_id,
        Student.is_active.is_(True)
    ).order_by(Student.full_name.asc())
    result = await db.execute(query)
    return result.scalars().all()

async def get_student_report_card(
    db: AsyncSession,
    student_id: uuid.UUID
) -> list[dict]:
    """Aggregates all exam results for the student joined to exams and subjects."""
    query = (
        select(
            Subject.id.label("subject_id"),
            Subject.name.label("subject_name"),
            Subject.code.label("subject_code"),
            Exam.name.label("exam_name"),
            Exam.total_marks.label("total_marks"),
            ExamResult.marks_obtained.label("marks_obtained"),
            ExamResult.grade.label("grade"),
            Exam.exam_date.label("exam_date")
        )
        .join(Exam, ExamResult.exam_id == Exam.id)
        .join(Subject, Exam.subject_id == Subject.id)
        .where(ExamResult.student_id == student_id)
        .order_by(Subject.name.asc(), Exam.exam_date.asc())
    )
    rows = (await db.execute(query)).all()

    # Group by subject
    subjects_map: dict[uuid.UUID, dict] = {}
    for r in rows:
        sub_id = r.subject_id
        if sub_id not in subjects_map:
            subjects_map[sub_id] = {
                "subject_id": sub_id,
                "subject_name": r.subject_name,
                "subject_code": r.subject_code,
                "total_marks": 0,
                "marks_obtained": 0,
                "exams": []
            }
        subjects_map[sub_id]["total_marks"] += r.total_marks
        subjects_map[sub_id]["marks_obtained"] += r.marks_obtained
        subjects_map[sub_id]["exams"].append({
            "exam_name": r.exam_name,
            "exam_date": r.exam_date,
            "total_marks": r.total_marks,
            "marks_obtained": r.marks_obtained,
            "grade": r.grade
        })

    report_card = []
    for sub in subjects_map.values():
        # Overall grade or latest exam grade
        latest_grade = sub["exams"][-1]["grade"] if sub["exams"] else "N/A"
        report_card.append({
            "subject_id": sub["subject_id"],
            "subject_name": sub["subject_name"],
            "subject_code": sub["subject_code"],
            "total_marks": sub["total_marks"],
            "marks_obtained": sub["marks_obtained"],
            "grade": latest_grade,
            "exams": sub["exams"]
        })

    return report_card

