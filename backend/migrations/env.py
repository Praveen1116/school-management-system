import asyncio
import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

# Ensure backend root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from config import settings
from database import Base

# Setup alias for module compatibility
from modules.classes import model as classes_model
sys.modules["modules.student_class_enrollments"] = classes_model
sys.modules["modules.student_class_enrollments.model"] = classes_model
sys.modules["modules.class_subject_assignments"] = classes_model
sys.modules["modules.class_subject_assignments.model"] = classes_model

# Explicitly import all 14 models before setting target_metadata
from modules.users.model import User
from modules.students.model import Student
from modules.teachers.model import Teacher
from modules.classes.model import Class
from modules.subjects.model import Subject
from modules.student_class_enrollments.model import StudentClassEnrollment
from modules.class_subject_assignments.model import ClassSubjectAssignment
from modules.attendance.model import AttendanceRecord
from modules.exams.model import GradingRule, Exam, ExamResult
from modules.fees.model import FeeInvoice, FeePayment
from modules.audit.model import AuditLog

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set metadata for autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = settings.DATABASE_URL_DIRECT
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode using asyncpg and direct connection string."""
    connectable = create_async_engine(
        settings.DATABASE_URL_DIRECT,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
