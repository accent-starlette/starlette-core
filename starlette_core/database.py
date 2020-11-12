import typing
from urllib.parse import SplitResult, parse_qsl, urlsplit

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from starlette.config import environ
from starlette.exceptions import HTTPException

metadata = sa.MetaData()


@as_declarative(metadata=metadata)
class Base:
    session: AsyncSession = None

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    @classmethod
    async def get(cls, ident):
        qs = sa.select(cls).where(cls.id == ident)
        results = await cls.session.execute(qs)
        return results.scalars().first()

    @classmethod
    async def get_or_404(cls, ident):
        result = await cls.get(ident)
        if not result:
            raise HTTPException(status_code=404)
        return result

    def __repr__(self):
        return f"<{self.__class__.__name__}, id={self.id}>"

    def __str__(self):
        return self.__repr__()

    # Default auto incrementing primary key field, overwrite as needed
    id = sa.Column(sa.Integer, primary_key=True)

    async def save(self) -> None:
        """ save the current instance """

        savepoint = await self.session.begin_nested()
        try:
            self.session.add(self)
            await savepoint.commit()
        except:
            await savepoint.rollback()
            raise

    async def delete(self) -> None:
        """ delete the current instance """

        savepoint = await self.session.begin_nested()
        try:
            self.session.delete(self)
            await savepoint.commit()
        except:
            await savepoint.rollback()
            raise

    # def can_be_deleted(self) -> bool:
    #     """
    #     Simple helper to check if the instance has entities
    #     that will prevent this from being deleted via a protected foreign key.
    #     """
    #     from sqlalchemy_utils import dependent_objects, get_referencing_foreign_keys

    #     deps = list(
    #         dependent_objects(
    #             self,
    #             (
    #                 fk
    #                 for fk in get_referencing_foreign_keys(self.__class__)
    #                 # On most databases RESTRICT is the default mode hence we
    #                 # check for None values also
    #                 if fk.ondelete == "RESTRICT" or fk.ondelete is None
    #             ),
    #         ).limit(1)
    #     )

    #     return not deps

    async def refresh_from_db(self) -> None:
        """ Refresh the current instance from the database """

        await self.session.refresh(self)


class Database:
    engine: AsyncEngine = None
    session: AsyncSession = None

    def __init__(self, url: "DatabaseURL", engine_kwargs: dict = {}) -> None:
        # configure the engine
        self.engine = create_async_engine(str(url), **engine_kwargs)
        self.session = AsyncSession(bind=self.engine)
        # configue base attrs
        Base.session = self.session

    async def create_all(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(metadata.create_all)

    async def drop_all(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(metadata.drop_all)

    async def truncate_all(self, force: bool = False) -> None:
        if not (environ.get("TESTING") == "TRUE" or force):
            raise Exception("can only truncate while testing or set to force")

        async with self.engine.begin() as conn:
            for table in reversed(metadata.sorted_tables):
                try:
                    await conn.execute(table.delete())
                except:
                    pass
            await conn.commit()


class _EmptyNetloc(str):
    def __bool__(self) -> bool:
        return True


class DatabaseURL:
    def __init__(self, url: typing.Union[str, "DatabaseURL"]):
        self._url = str(url)

    @property
    def components(self) -> SplitResult:
        if not hasattr(self, "_components"):
            self._components = urlsplit(self._url)
        return self._components

    @property
    def dialect(self) -> str:
        return self.components.scheme.split("+")[0]

    @property
    def driver(self) -> str:
        if "+" not in self.components.scheme:
            return ""
        return self.components.scheme.split("+", 1)[1]

    @property
    def username(self) -> typing.Optional[str]:
        return self.components.username

    @property
    def password(self) -> typing.Optional[str]:
        return self.components.password

    @property
    def hostname(self) -> typing.Optional[str]:
        return self.components.hostname

    @property
    def port(self) -> typing.Optional[int]:
        return self.components.port

    @property
    def netloc(self) -> typing.Optional[str]:
        return self.components.netloc

    @property
    def database(self) -> str:
        return self.components.path.lstrip("/")

    @property
    def options(self) -> dict:
        if not hasattr(self, "_options"):
            self._options = dict(parse_qsl(self.components.query))
        return self._options

    def replace(self, **kwargs: typing.Any) -> "DatabaseURL":
        if (
            "username" in kwargs
            or "password" in kwargs
            or "hostname" in kwargs
            or "port" in kwargs
        ):
            hostname = kwargs.pop("hostname", self.hostname)
            port = kwargs.pop("port", self.port)
            username = kwargs.pop("username", self.username)
            password = kwargs.pop("password", self.password)

            netloc = hostname
            if port is not None:
                netloc += f":{port}"
            if username is not None:
                userpass = username
                if password is not None:
                    userpass += f":{password}"
                netloc = f"{userpass}@{netloc}"

            kwargs["netloc"] = netloc

        if "database" in kwargs:
            kwargs["path"] = "/" + kwargs.pop("database")

        if "dialect" in kwargs or "driver" in kwargs:
            dialect = kwargs.pop("dialect", self.dialect)
            driver = kwargs.pop("driver", self.driver)
            kwargs["scheme"] = f"{dialect}+{driver}" if driver else dialect

        if not kwargs.get("netloc", self.netloc):
            # Using an empty string that evaluates as True means we end
            # up with URLs like `sqlite:///database` instead of `sqlite:/database`
            kwargs["netloc"] = _EmptyNetloc()

        components = self.components._replace(**kwargs)
        return self.__class__(components.geturl())

    def __str__(self) -> str:
        return self._url

    def __repr__(self) -> str:
        url = str(self)
        if self.password:
            url = str(self.replace(password="********"))
        return f"{self.__class__.__name__}({repr(url)})"

    def __eq__(self, other: typing.Any) -> bool:
        return str(self) == str(other)
