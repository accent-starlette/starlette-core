import pytest
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException

from starlette_core.database import Base


class User(Base):
    name = sa.Column(sa.String(50), unique=True)


@pytest.mark.asyncio
async def test_database(db, conn):

    # connects ok
    async with db.engine.begin() as conn:

        def tbls(conn):
            return sa.inspect(conn).get_table_names()

        # can create tables
        await db.create_all()
        assert "user" in await conn.run_sync(tbls)

        # can drop tables
        await db.drop_all()
        assert [] == await conn.run_sync(tbls)


@pytest.mark.asyncio
async def test_database__session_usage(db, conn):
    await db.create_all()

    async with AsyncSession(conn) as session:
        user = User(name="bill")
        async with session.begin():
            session.add(user)
        await session.commit()


@pytest.mark.asyncio
async def test_database__session_usage_1(db, conn):
    await db.create_all()

    async with AsyncSession(conn) as session:
        user = User(name="bill")
        async with session.begin():
            session.add(user)
        await session.commit()


@pytest.mark.asyncio
async def test_declarative_base__save(db):
    await db.create_all()

    user = User(name="ted")
    await user.save()

    qs = sa.select(User).where(User.name == "ted")
    result = await User.session.execute(qs)
    assert result.scalars().first() == user


@pytest.mark.asyncio
async def test_declarative_base__delete(db):
    await db.create_all()

    user = User(name="ted")
    await user.save()

    await user.delete()

    qs = sa.select(User).where(User.name == "ted")
    result = await User.session.execute(qs)
    assert result.scalars().first() is None


@pytest.mark.asyncio
async def test_declarative_base__refresh_from_db(db):
    await db.create_all()

    user = User(name="ted")
    await user.save()
    user.name = "sam"

    await user.refresh_from_db()
    assert user.name == "ted"


# @pytest.mark.asyncio
# async def test_declarative_base__can_be_deleted(db):
#     class OrderA(Base):
#         user_id = sa.Column(
#             sa.Integer,
#             sa.ForeignKey(User.id)
#         )

#     class OrderB(Base):
#         user_id = sa.Column(
#             sa.Integer,
#             sa.ForeignKey(User.id, ondelete="SET NULL"),
#             nullable=True
#         )

#     class OrderC(Base):
#         user_id = sa.Column(
#             sa.Integer,
#             sa.ForeignKey(User.id, ondelete="CASCADE")
#         )

#     class OrderD(Base):
#         user_id = sa.Column(
#             sa.Integer,
#             sa.ForeignKey(User.id, ondelete="RESTRICT")
#         )

#     await db.create_all()

#     user = User(name="ted")
#     await user.save()

#     assert user.can_be_deleted()

#     # default

#     order = OrderA(user_id=user.id)
#     await order.save()
#     assert not user.can_be_deleted()

#     await order.delete()
#     assert user.can_be_deleted()

#     # set null

#     order = OrderB(user_id=user.id)
#     await order.save()
#     assert user.can_be_deleted()

#     # cascade

#     order = OrderC(user_id=user.id)
#     await order.save()
#     assert user.can_be_deleted()

#     # restrict

#     order = OrderD(user_id=user.id)
#     await order.save()
#     assert not user.can_be_deleted()

#     await order.delete()
#     assert user.can_be_deleted()


@pytest.mark.asyncio
async def test_declarative_base__repr(db):
    await db.create_all()

    user = User()

    assert user.__tablename__ == "user"
    assert repr(user) == f"<User, id={user.id}>"
    assert str(user) == f"<User, id={user.id}>"


@pytest.mark.asyncio
async def test_declarative_base__get(db):
    await db.create_all()

    user = User(name="ted")
    await user.save()

    # get
    assert await User.get(user.id) == user

    # get is none
    assert await User.get(1000) is None


@pytest.mark.asyncio
async def test_declarative_base__get_or_404(db):
    await db.create_all()

    user = User(name="ted")
    await user.save()

    # get_or_404
    assert await User.get_or_404(user.id) == user

    # get_or_404 raises http exception when no result found
    with pytest.raises(HTTPException) as e:
        await User.get_or_404(1000)
    assert e.value.status_code == 404
