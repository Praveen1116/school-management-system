import uuid
from sqlalchemy import String, Integer, ForeignKey, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

class Class(Base):
    __tablename__ = "classes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()")
    )
    name: Mapped[str] = mapped_column(
        String,
        nullable=False
    )
    section: Mapped[str] = mapped_column(
        String,
        nullable=False
    )
    academic_year: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint("name", "section", "academic_year", name="uq_class_name_section_year"),
    )


class StudentClassEnrollment(Base):
    __tablename__ = "student_class_enrollments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()")
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("students.id"),
        nullable=False
    )
    class_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("classes.id"),
        nullable=False
    )
    academic_year: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint("student_id", "class_id", "academic_year", name="uq_student_class_year"),
    )


class ClassSubjectAssignment(Base):
    __tablename__ = "class_subject_assignments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()")
    )
    class_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("classes.id"),
        nullable=False
    )
    subject_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("subjects.id"),
        nullable=False
    )
    teacher_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teachers.id"),
        nullable=False
    )
    academic_year: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint("class_id", "subject_id", "academic_year", name="uq_class_subject_year"),
    )

