import pytest
import sqlalchemy as sa
from starlette.exceptions import HTTPException

from starlette_core.database import Base, Session


class User(Base):
    name = sa.Column(sa.String(50))


def test_database(db):
    # connects ok
    db.engine.connect()

    # can create tables
    db.create_all()
    assert "user" in db.engine.table_names()

    # can drop tables
    db.drop_all()
    assert [] == db.engine.table_names()


def test_database__truncate_of_db(db):
    db.create_all()

    user = User(name="bill")
    user.save()

    assert User.query.count() == 1

    db.truncate_all(force=True)

    assert User.query.count() == 0


def test_session(db):
    db.create_all()

    # basic session usage
    user = User(name="bill")

    session = Session()
    session.add(user)
    session.commit()
    session.close()


def test_declarative_base__save(db):
    db.create_all()

    user = User(name="ted")
    user.save()

    assert User.query.get(user.id) == user


def test_declarative_base__delete(db):
    db.create_all()

    user = User(name="ted")
    user.save()

    user.delete()
    assert User.query.get(user.id) is None


def test_declarative_base__refresh_from_db(db):
    db.create_all()

    user = User(name="ted")
    user.save()
    user.name = "sam"

    user.refresh_from_db()
    assert user.name == "ted"


def test_declarative_base__repr(db):
    db.create_all()

    user = User()

    assert user.__tablename__ == "user"
    assert repr(user) == f"<User, id={user.id}>"
    assert str(user) == f"<User, id={user.id}>"


def test_declarative_base__query(db):
    db.create_all()

    user = User(name="ted")
    user.save()

    # get_or_404
    assert User.query.get_or_404(user.id) == user

    # get_or_404 raises http exception when no result found
    with pytest.raises(HTTPException) as e:
        User.query.get_or_404(1000)
    assert e.value.status_code == 404
