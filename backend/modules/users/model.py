import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()")
    )
    email: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
        index=True
    )
    full_name: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )
    password_hash: Mapped[str] = mapped_column(
        String,
        nullable=False
    )
    role: Mapped[str] = mapped_column(
        String,
        nullable=False  # Values: admin, teacher, guardian
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=text("true"),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False
    )

