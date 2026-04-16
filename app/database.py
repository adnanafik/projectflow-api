"""Async SQLAlchemy engine, session factory, and dependency injection."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.models.base import Base

engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an async database session."""
    async with async_session() as session:
        yield session


async def create_all_tables() -> None:
    """Create all tables defined in ORM models. Used on startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
