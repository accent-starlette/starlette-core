import pytest
from starlette.exceptions import HTTPException

from starlette_core.database import Base, Session


class User(Base):
    pass


def test_database(db):
    # connects ok
    db.engine.connect()

    # can create tables
    db.create_all()
    assert "user" in db.engine.table_names()

    # can drop tables
    db.drop_all()
    assert [] == db.engine.table_names()


def test_session(db):
    db.create_all()

    # basic session usage
    session = Session()
    session.add(User())
    session.commit()
    session.close()


def test_declarative_base(db):
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


def test_truncate_of_db(db):
    user = User()
    user.save()

    assert User.query.count() == 1

    db.truncate_all(force=True)

    assert User.query.count() == 0
