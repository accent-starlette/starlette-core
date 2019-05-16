import pytest
from starlette.exceptions import HTTPException

from starlette_core.database import Base, Database, DatabaseURL, Session


class User(Base):
    pass


url = DatabaseURL("sqlite://")
db = Database(url)


def test_database():
    # connects ok
    db.engine.connect()

    # can create tables
    db.create_all()
    assert ["user"] == db.engine.table_names()

    # can drop tables
    db.drop_all()
    assert [] == db.engine.table_names()


def test_session():
    db.create_all()

    # basic session usage
    session = Session()
    session.add(User())
    session.commit()
    session.close()


def test_declarative_base():
    db.create_all()

    # save
    user = User()
    user.save()
    assert User.query.get(user.id) == user

    # str and repr
    assert user.__tablename__ == "user"
    assert repr(user) == f"<User, id={user.id}>"
    assert str(user) == f"<User, id={user.id}>"

    # built in queries

    # get_or_404
    assert User.query.get_or_404(user.id) == user

    # get_or_404 raises http exception when no result found
    with pytest.raises(HTTPException) as e:
        User.query.get_or_404(1000)
    assert e.value.status_code == 404

    # delete
    user.delete()
    assert User.query.get(user.id) is None
