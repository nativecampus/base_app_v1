from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import worker_session


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
