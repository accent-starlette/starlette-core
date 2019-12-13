# Database

Within most projects there is a need for a database. Within `starlette_core` we use SQLAlchemy.

## Declarative Base

Due to the fact we have created other projects that all inherit from this package such as [starlette-auth](https://github.com/accent-starlette/starlette-auth) there needs to be a central place that all predefined tables can inherit from a declarative base class ([see the docs](https://docs.sqlalchemy.org/en/13/orm/extensions/declarative/basic_use.html)).

The `starlette_core.database.Base` class consists of:

```python
class BaseQuery(Query):
    def get_or_404(self, ident):
        """
        performs a query.get or raises `starlette.exceptions.HTTPException`
        if not found.
        """

@as_declarative(metadata=metadata)
class Base:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    def __repr__(self):
        return f"<{self.__class__.__name__}, id={self.id}>"

    def __str__(self):
        return self.__repr__()

    # Default auto incrementing primary key field
    # overwrite as needed
    id = sa.Column(sa.Integer, primary_key=True)

    # Convenience property to query the database for instances of this model
    # using the current session. Equivalent to ``db.session.query(Model)``
    query: BaseQuery

    def save(self) -> None:
        """ save the current instance """

    def delete(self) -> None:
        """ delete the current instance """

    def can_be_deleted(self) -> bool:
        """
        Simple helper to check if the instance has entities
        that will prevent this from being deleted via a protected foreign key.
        """

    def refresh_from_db(self) -> None:
        """ Refresh the current instance from the database """
```

This class should be used in all sqlalchemy tables like so:

```python
import sqlalchemy as sa
from starlette_core.database import Base

class User(Base):
    email = sa.Column(sa.String(100), nullable=False, index=True, unique=True)
```

### Methods

All tables inheriting from `Base` will have acess to the class' functionallity. This includes `.query`, `.save()`, and `.delete()`.

It is important that all tables(base) are imported from all packages when used:

```python
from db import database
from tables import User

user = User.query.first()

user.email = "user@example.com"
user.save()
user.delete()
```


## Your Project Structure

It's best to have a central place to keep a reference to your database. 
Assuming you have a `db.py` file in the root of your apps structure and the contents
are as follows:

```python
from starlette_core.database import Database, DatabaseURL, metadata
from app.settings import DATABASE_URL

url = DatabaseURL("sqlite:///./db.sqlite3")

# set engine config options
engine_kwargs = {}

# setup the database
database = Database(DATABASE_URL, engine_kwargs=engine_kwargs)

# once the db is initialised you can import any project 
# and external tables into this file.

# the metadata imported above will be the complete metadata 
# used for your db for the likes of alembic migrations.
from my_project import tables
from some_other_project import tables
```

## The Database Class

The `starlette_core.database.Database` class is what manages the connection to the database.

```python
class Database:
    engine = None

    def create_all(self) -> None:
        """ create all tables """

    def drop_all(self) -> None:
        """ drop all tables """

    def truncate_all(self, force: bool = False) -> None:
        """ truncate all tables """
```

Which when defined as above you can run commands like `database.create_all()` 
or `database.engine.execute("SELECT .....")` on.

## Sessions

While tables that inherit from `starlette_core.database.Base` will include useful
helpers like `save()` and `delete()`, these internally just use a `Session` object ([see the docs](https://docs.sqlalchemy.org/en/13/orm/session.html)).

This can be used directly which is particually helpful if you want to save multiple instances at the
same time.

```python
from starlette_core.database import Session

session = Session()

instance = User(email="admin@example.com")

try:
    session.add(instance)
    session.commit()
except:
    session.rollback()
```

## Middleware

!!! warning "Using the `DatabaseMiddleware`"

    If you are using the database functionality provided by this package it is important to use the middleware to correctly handle sessions.
    [See docs](/middleware).