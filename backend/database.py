from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from config import settings

# Application engine uses the pooled connection string (port 6543 on Neon)
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Test connection viability before handing to query
    echo=False,
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

# Declarative Base for all SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Dependency providing an async database session per request
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

