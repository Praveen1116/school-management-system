import uuid
from datetime import date, datetime, timezone
from sqlalchemy import String, Integer, Date, DateTime, ForeignKey, UniqueConstraint, text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

class GradingRule(Base):
    __tablename__ = "grading_rules"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()")
    )
    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
        index=True  # e.g. "Standard 2026"
    )
    grade_label: Mapped[str] = mapped_column(
        String,
        nullable=False  # e.g. "A", "B", "C", "D", "F"
    )
    min_marks: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    max_marks: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )


class Exam(Base):
    __tablename__ = "exams"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()")
    )
    subject_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("subjects.id"),
        nullable=False
    )
    grading_rule_set_name: Mapped[str] = mapped_column(
        String,
        nullable=False
    )
    name: Mapped[str] = mapped_column(
        String,
        nullable=False
    )
    total_marks: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    exam_date: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )


class ExamResult(Base):
    __tablename__ = "exam_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()")
    )
    exam_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("exams.id"),
        nullable=False
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("students.id"),
        nullable=False
    )
    entered_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teachers.id"),
        nullable=False
    )
    marks_obtained: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    grade: Mapped[str] = mapped_column(
        String,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint("exam_id", "student_id", name="uq_exam_student"),
    )

