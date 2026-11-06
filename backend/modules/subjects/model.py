import uuid
from sqlalchemy import String, Integer, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

class Subject(Base):
    __tablename__ = "subjects"

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
    code: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
        index=True
    )
    total_marks: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

