import importlib

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.database import _to_async_url, get_db
from app.main import app
from app.models.base import Base

_url = _to_async_url(settings.DATABASE_URL)


@pytest.fixture(scope="session", autouse=True)
async def _setup_db():
    """Create all tables before tests, drop after."""
    # Import test modules that define models so their tables are registered
    importlib.import_module("tests.test_audit")

    engine = create_async_engine(_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture(scope="session")
async def _session_factory():
    engine = create_async_engine(_url)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    yield factory
    await engine.dispose()


@pytest.fixture
async def db(_session_factory):
    """Yield a database session that rolls back after each test."""
    async with _session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(db):
    """Async HTTP client with database dependency overridden."""

    async def _override_db():
        yield db

    app.dependency_overrides[get_db] = _override_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
