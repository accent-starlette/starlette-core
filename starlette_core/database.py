import sqlalchemy as sa
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import Query, scoped_session, sessionmaker
from starlette.exceptions import HTTPException

metadata = sa.MetaData()
Session = scoped_session(sessionmaker())


class BaseQuery(Query):
    def get_or_404(self, ident):
        """ performs a query.get or raises a 404 if not found """

        qs = self.get(ident)
        if not qs:
            raise HTTPException(status_code=404)
        return qs


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

    def save(self):
        """ save the current instance """

        session = Session()

        try:
            session.add(self)
            session.commit()
        except:
            session.rollback()
            raise

    def delete(self):
        """ delete the current instance """

        session = Session()

        try:
            session.delete(self)
            session.commit()
        except:
            session.rollback()
            raise


class Database:
    engine = None

    def __init__(self, url: str) -> None:
        # configure the engine
        self.engine = sa.create_engine(url)
        Session.configure(bind=self.engine)
        # setup the model.query property
        Base.query = Session.query_property(query_cls=BaseQuery)

    def create_all(self) -> None:
        metadata.create_all(self.engine)

    def drop_all(self) -> None:
        metadata.drop_all(self.engine)
