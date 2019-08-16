import pytest

from starlette_core.database import Database, DatabaseURL

url = DatabaseURL("sqlite://")
database = Database(url)


@pytest.fixture()
def db():
    yield database
    database.truncate_all(force=True)
