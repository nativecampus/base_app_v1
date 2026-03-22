"""Drop and recreate all tables. Usage: python -m scripts.db_reset [--yes]"""

import asyncio
import sys

from sqlalchemy.ext.asyncio import create_async_engine

from app.database import _to_async_url
from app.config import settings
from app.models.base import Base


async def reset():
    engine = create_async_engine(_to_async_url(settings.DATABASE_URL))
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    print("Database reset complete.")


def main():
    if "--yes" not in sys.argv:
        db = settings.DATABASE_URL.rsplit("/", 1)[-1]
        answer = input(f"This will drop all tables in '{db}'. Continue? [y/N] ")
        if answer.lower() != "y":
            print("Aborted.")
            return
    asyncio.run(reset())


if __name__ == "__main__":
    main()
