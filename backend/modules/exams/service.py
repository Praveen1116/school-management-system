import uuid
from typing import Sequence
from datetime import date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from modules.exams.model import GradingRule, Exam, ExamResult
from modules.classes.model import ClassSubjectAssignment
from modules.students.model import Student

# --- Grading Rules ---

async def list_grading_rules(db: AsyncSession) -> Sequence[GradingRule]:
    query = select(GradingRule).order_by(GradingRule.name.asc(), GradingRule.min_marks.desc())
    return (await db.execute(query)).scalars().all()

async def get_grading_rule_by_id(db: AsyncSession, rule_id: uuid.UUID) -> GradingRule | None:
    result = await db.execute(select(GradingRule).where(GradingRule.id == rule_id))
    return result.scalar_one_or_none()

async def create_grading_rule(
    db: AsyncSession,
    name: str,
    grade_label: str,
    min_marks: int,
    max_marks: int
) -> GradingRule:
    rule = GradingRule(
        name=name,
        grade_label=grade_label,
        min_marks=min_marks,
        max_marks=max_marks
    )
    db.add(rule)
    await db.flush()
    return rule

async def update_grading_rule(
    db: AsyncSession,
    rule: GradingRule,
    name: str | None = None,
    grade_label: str | None = None,
    min_marks: int | None = None,
    max_marks: int | None = None
) -> GradingRule:
    if name is not None:
        rule.name = name
    if grade_label is not None:
        rule.grade_label = grade_label
    if min_marks is not None:
        rule.min_marks = min_marks
    if max_marks is not None:
        rule.max_marks = max_marks
    await db.flush()
    return rule

async def compute_grade(db: AsyncSession, rule_set_name: str, marks: int) -> str | None:
    """Finds matching grade label where min_marks <= marks <= max_marks."""
    query = select(GradingRule.grade_label).where(
        GradingRule.name == rule_set_name,
        GradingRule.min_marks <= marks,
        GradingRule.max_marks >= marks
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()

# --- Exams ---

async def get_exam_by_id(db: AsyncSession, exam_id: uuid.UUID) -> Exam | None:
    result = await db.execute(select(Exam).where(Exam.id == exam_id))
    return result.scalar_one_or_none()

async def list_exams(
    db: AsyncSession,
    teacher_id: uuid.UUID | None = None
) -> Sequence[Exam]:
    """Admin sees all exams; Teacher sees only exams for assigned subjects."""
    if teacher_id is not None:
        query = (
            select(Exam)
            .join(ClassSubjectAssignment, Exam.subject_id == ClassSubjectAssignment.subject_id)
            .where(ClassSubjectAssignment.teacher_id == teacher_id)
            .distinct()
            .order_by(Exam.exam_date.desc())
        )
    else:
        query = select(Exam).order_by(Exam.exam_date.desc())

    result = await db.execute(query)
    return result.scalars().all()

async def create_exam(
    db: AsyncSession,
    subject_id: uuid.UUID,
    grading_rule_set_name: str,
    name: str,
    total_marks: int,
    exam_date: date
) -> Exam:
    exam = Exam(
        subject_id=subject_id,
        grading_rule_set_name=grading_rule_set_name,
        name=name,
        total_marks=total_marks,
        exam_date=exam_date
    )
    db.add(exam)
    await db.flush()
    return exam

async def update_exam(
    db: AsyncSession,
    exam: Exam,
    name: str | None = None,
    total_marks: int | None = None,
    exam_date: date | None = None,
    grading_rule_set_name: str | None = None
) -> Exam:
    if name is not None:
        exam.name = name
    if total_marks is not None:
        exam.total_marks = total_marks
    if exam_date is not None:
        exam.exam_date = exam_date
    if grading_rule_set_name is not None:
        exam.grading_rule_set_name = grading_rule_set_name
    await db.flush()
    return exam

# --- Results ---

async def get_result_by_id(db: AsyncSession, result_id: uuid.UUID) -> ExamResult | None:
    result = await db.execute(select(ExamResult).where(ExamResult.id == result_id))
    return result.scalar_one_or_none()

async def get_result_by_exam_and_student(
    db: AsyncSession,
    exam_id: uuid.UUID,
    student_id: uuid.UUID
) -> ExamResult | None:
    query = select(ExamResult).where(
        ExamResult.exam_id == exam_id,
        ExamResult.student_id == student_id
    )
    return (await db.execute(query)).scalar_one_or_none()

async def list_exam_results(db: AsyncSession, exam_id: uuid.UUID) -> list[dict]:
    query = (
        select(ExamResult, Student.full_name, Student.roll_number)
        .join(Student, ExamResult.student_id == Student.id)
        .where(ExamResult.exam_id == exam_id)
        .order_by(Student.roll_number.asc())
    )
    rows = (await db.execute(query)).all()
    return [
        {
            "id": r.id,
            "exam_id": r.exam_id,
            "student_id": r.student_id,
            "student_name": name,
            "roll_number": roll,
            "entered_by": r.entered_by,
            "marks_obtained": r.marks_obtained,
            "grade": r.grade,
            "created_at": r.created_at
        }
        for r, name, roll in rows
    ]

async def create_result(
    db: AsyncSession,
    exam_id: uuid.UUID,
    student_id: uuid.UUID,
    entered_by: uuid.UUID,
    marks_obtained: int,
    grade: str
) -> ExamResult:
    result = ExamResult(
        exam_id=exam_id,
        student_id=student_id,
        entered_by=entered_by,
        marks_obtained=marks_obtained,
        grade=grade
    )
    db.add(result)
    await db.flush()
    return result

async def update_result(
    db: AsyncSession,
    result: ExamResult,
    marks_obtained: int,
    grade: str
) -> ExamResult:
    result.marks_obtained = marks_obtained
    result.grade = grade
    await db.flush()
    return result

