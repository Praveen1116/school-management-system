import sys
from pathlib import Path

# Add backend directory to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select, pool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from config import settings
from database import Base, get_db
from main import app
from seed import seed_data
from modules.users.model import User
from modules.auth.service import create_access_token

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_database():
    """Seeds test data before tests run."""
    try:
        await seed_data()
    except Exception as e:
        print(f"Database setup note: {e}")
    yield

@pytest_asyncio.fixture
async def db_session():
    """Creates a fresh database session per test using NullPool."""
    engine = create_async_engine(settings.DATABASE_URL, poolclass=pool.NullPool)
    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    await engine.dispose()

@pytest_asyncio.fixture
async def client():
    """Async test HTTP client with per-test db session override."""
    engine = create_async_engine(settings.DATABASE_URL, poolclass=pool.NullPool)
    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with session_factory() as session:
            try:
                yield session
            finally:
                await session.close()

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as ac:
        yield ac
    app.dependency_overrides.clear()
    await engine.dispose()

@pytest_asyncio.fixture
async def admin_token(db_session: AsyncSession):
    user = (await db_session.execute(select(User).where(User.email == "admin@school.demo"))).scalar_one()
    return create_access_token({"sub": str(user.id), "role": user.role})

@pytest_asyncio.fixture
async def teacher_a_token(db_session: AsyncSession):
    user = (await db_session.execute(select(User).where(User.email == "teacher.a@school.demo"))).scalar_one()
    return create_access_token({"sub": str(user.id), "role": user.role})

@pytest_asyncio.fixture
async def teacher_b_token(db_session: AsyncSession):
    user = (await db_session.execute(select(User).where(User.email == "teacher.b@school.demo"))).scalar_one()
    return create_access_token({"sub": str(user.id), "role": user.role})

@pytest_asyncio.fixture
async def guardian_a_token(db_session: AsyncSession):
    user = (await db_session.execute(select(User).where(User.email == "guardian.a@school.demo"))).scalar_one()
    return create_access_token({"sub": str(user.id), "role": user.role})

@pytest_asyncio.fixture
async def guardian_b_token(db_session: AsyncSession):
    user = (await db_session.execute(select(User).where(User.email == "guardian.b@school.demo"))).scalar_one()
    return create_access_token({"sub": str(user.id), "role": user.role})
