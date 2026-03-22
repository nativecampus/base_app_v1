import re
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings


def _to_async_url(url: str) -> str:
    """Convert a PostgreSQL URL to use the asyncpg driver."""
    return re.sub(r"^postgresql(\+psycopg2)?://", "postgresql+asyncpg://", url)


_url = _to_async_url(settings.DATABASE_URL)
engine = create_async_engine(_url)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    """FastAPI dependency that yields an async database session."""
    async with async_session() as session:
        yield session


def _create_engine(url: str):
    """Create a new async engine — used by workers that need their own event loop."""
    return create_async_engine(_to_async_url(url))


@asynccontextmanager
async def worker_session():
    """Create a standalone session for background workers.

    Workers run in a separate process/event loop, so they need their own engine.
    """
    worker_engine = _create_engine(settings.DATABASE_URL)
    factory = async_sessionmaker(
        worker_engine, class_=AsyncSession, expire_on_commit=False
    )
    try:
        async with factory() as session:
            yield session
    finally:
        await worker_engine.dispose()
