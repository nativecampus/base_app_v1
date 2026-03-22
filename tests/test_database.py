from sqlalchemy import text


async def test_db_connection(db):
    result = await db.execute(text("SELECT 1"))
    assert result.scalar() == 1
