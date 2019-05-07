import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import Query, scoped_session, sessionmaker


class BaseModel:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    def __repr__(self):
        return f'<{self.__class__.__name__}, id={self.id}>'

    def __str__(self):
        return self.__repr__()

    # Default auto incrementing primary key field
    # overwrite as needed
    id = sa.Column(sa.Integer, primary_key=True)

    # Convenience property to query the database for instances of this model
    # using the current session. Equivalent to ``db.session.query(Model)``
    query: Query = None


metadata = sa.MetaData()
Base = declarative_base(cls=BaseModel, metadata=metadata)
Session = scoped_session(sessionmaker())


class Database:
    engine = None

    def __init__(self, url: str) -> None:
        # configure the engine
        self.engine = sa.create_engine(url)
        Session.configure(bind=self.engine)
        # setup the model.query property
        Base.query = Session.query_property()

    def create_all(self) -> None:
        metadata.create_all(self.engine)

    def drop_all(self) -> None:
        metadata.drop_all(self.engine)