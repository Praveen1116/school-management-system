import uuid
from datetime import date, datetime, timezone
from sqlalchemy import String, Date, DateTime, ForeignKey, UniqueConstraint, Index, text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

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
    recorded_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teachers.id"),
        nullable=False
    )
    attendance_date: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )
    session: Mapped[str] = mapped_column(
        String,
        nullable=False  # Values: full_day, morning, afternoon
    )
    status: Mapped[str] = mapped_column(
        String,
        nullable=False  # Values: present, absent, late
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint("student_id", "attendance_date", "session", name="uq_student_date_session"),
        Index("ix_attendance_class_date", "class_id", "attendance_date"),
        Index("ix_attendance_student_date", "student_id", "attendance_date"),
    )

