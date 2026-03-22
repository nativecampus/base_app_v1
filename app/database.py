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


_worker_engine_ref: list = []


def _get_worker_engine():
    """Return a shared engine for background workers, creating it on first use."""
    if not _worker_engine_ref:
        _worker_engine_ref.append(
            create_async_engine(_to_async_url(settings.DATABASE_URL))
        )
    return _worker_engine_ref[0]


async def dispose_worker_engine() -> None:
    """Dispose the shared worker engine if it exists."""
    if _worker_engine_ref:
        engine = _worker_engine_ref.pop()
        await engine.dispose()


@asynccontextmanager
async def worker_session():
    """Create a standalone session for background workers.

    Workers run in a separate process/event loop, so they need their own engine.
    The engine is lazily created and reused across calls within the same process.
    """
    worker_engine = _get_worker_engine()
    factory = async_sessionmaker(
        worker_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with factory() as session:
        yield session
