from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import worker_session, _worker_engine_ref, dispose_worker_engine


async def test_db_connection(db):
    """Verify the test database session can execute a query."""
    result = await db.execute(text("SELECT 1"))
    assert result.scalar() == 1


async def test_worker_session_as_context_manager():
    """Verify worker_session works as an async context manager."""
    async with worker_session() as session:
        assert isinstance(session, AsyncSession)
        result = await session.execute(text("SELECT 1"))
        assert result.scalar() == 1


async def test_worker_session_reuses_engine():
    """Consecutive worker_session calls share the same engine instance."""
    async with worker_session() as s1:
        engine1 = s1.bind
    async with worker_session() as s2:
        engine2 = s2.bind
    assert engine1 is engine2


async def test_dispose_worker_engine_clears_ref():
    """dispose_worker_engine disposes the engine and clears the ref list."""
    async with worker_session() as session:
        await session.execute(text("SELECT 1"))
    assert len(_worker_engine_ref) == 1
    await dispose_worker_engine()
    assert len(_worker_engine_ref) == 0


async def test_dispose_worker_engine_is_idempotent():
    """Calling dispose_worker_engine when no engine exists does nothing."""
    _worker_engine_ref.clear()
    await dispose_worker_engine()
    assert len(_worker_engine_ref) == 0
