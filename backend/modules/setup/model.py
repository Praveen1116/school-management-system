import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

class School(Base):
    __tablename__ = "schools"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()")
    )
    school_name: Mapped[str] = mapped_column(
        String,
        nullable=False
    )
    school_code: Mapped[str] = mapped_column(
        String,
        nullable=False,
        unique=True,
        index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False
    )

