"""Seed database with initial data. Usage: python -m scripts.seed_all [--only name ...]

Add seed functions to SEEDERS dict. Each receives an AsyncSession.
"""

import asyncio
import sys

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import _to_async_url
from app.config import settings


async def seed_settings(session: AsyncSession):
    """Seed application settings. Customise per project."""
    pass


SEEDERS = {
    "settings": seed_settings,
}


async def run(only: list[str] | None = None):
    engine = create_async_engine(_to_async_url(settings.DATABASE_URL))
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    targets = {k: v for k, v in SEEDERS.items() if k in only} if only else SEEDERS

    async with factory() as session:
        for name, seeder in targets.items():
            print(f"Seeding {name}...")
            await seeder(session)
            await session.commit()
            print(f"  {name} done.")

    await engine.dispose()
    print("Seeding complete.")


def main():
    only = None
    if "--only" in sys.argv:
        idx = sys.argv.index("--only")
        only = sys.argv[idx + 1:]
        if not only:
            print("--only requires at least one seeder name")
            print(f"Available: {', '.join(SEEDERS.keys())}")
            return
    asyncio.run(run(only))


if __name__ == "__main__":
    main()
