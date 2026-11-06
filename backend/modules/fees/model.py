import uuid
from datetime import date, datetime, timezone
from sqlalchemy import String, Integer, Date, DateTime, ForeignKey, text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

class FeeInvoice(Base):
    __tablename__ = "fee_invoices"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()")
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("students.id"),
        nullable=False,
        index=True
    )
    description: Mapped[str] = mapped_column(
        String,
        nullable=False
    )
    amount_due: Mapped[int] = mapped_column(
        Integer,
        nullable=False  # Stored in paise
    )
    due_date: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False
    )


class FeePayment(Base):
    __tablename__ = "fee_payments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()")
    )
    invoice_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fee_invoices.id"),
        nullable=False,
        index=True
    )
    amount_paid: Mapped[int] = mapped_column(
        Integer,
        nullable=False  # Stored in paise
    )
    payment_ref: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
        index=True
    )
    paid_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False
    )

