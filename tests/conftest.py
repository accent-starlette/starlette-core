import pytest

from starlette_core.database import Database, DatabaseURL

url = DatabaseURL("sqlite://")
database = Database(url)


@pytest.fixture()
async def conn():
    async with database.engine.begin() as conn:
        yield conn
        await conn.rollback()


@pytest.fixture()
async def db():
    yield database
    await database.truncate_all(force=True)
