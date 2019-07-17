import datetime

import sqlalchemy as sa
from sqlalchemy import event, orm
from sqlalchemy.dialects.postgresql import ENUM, JSON

from ..database import Base
from ..middleware import get_request


class AuditLog(Base):
    discriminator = sa.Column(sa.String(255))
    parent_id = sa.Column(sa.Integer)
    operation = sa.Column(ENUM("INSERT", "DELETE", "UPDATE", name="operation"))
    created_on = sa.Column(
        sa.DateTime, nullable=False, default=datetime.datetime.utcnow
    )
    created_by_id = sa.Column(sa.Integer, sa.ForeignKey("user.id"), nullable=True)
    data = sa.Column(JSON)

    created_by = orm.relationship("User")

    @property
    def parent(self):
        """ Instance the audit log item belongs too """

        return getattr(self, "parent_%s" % self.discriminator)


class HasAuditLog:
    """
    Mixin that activates the audit log for a model.
    Provides access to instance.auditlog

    class MyModel(HasAuditLog, Base):
        pass
    """


@event.listens_for(HasAuditLog, "mapper_configured", propagate=True)
def setup_listener(mapper, class_):
    """
    Creates the mapping between an instance of a model that inherits from 'HasAuditLog'
    and the 'AuditLog' itself.

    Provides access to `instance.auditlog`.
    """

    name = class_.__name__
    discriminator = name.lower()

    class_.auditlog = orm.relationship(
        AuditLog,
        primaryjoin=sa.and_(
            class_.id == orm.foreign(orm.remote(AuditLog.parent_id)),
            AuditLog.discriminator == discriminator,
        ),
        backref=orm.backref(
            "parent_%s" % discriminator,
            primaryjoin=orm.remote(class_.id) == orm.foreign(AuditLog.parent_id),
        ),
        order_by="AuditLog.created_on",
        passive_deletes=True,
    )


def add_auditlog_entry(mapper, connection, target, operation):
    copied = target.__dict__.copy()
    prepared = dict([(key, copied.get(key)) for key in mapper.columns.keys()])
    request = get_request()

    user_id = None
    if "user" in request:
        user_id = getattr(request["user"], "id")

    connection.execute(
        AuditLog.__table__.insert().values(
            {
                "discriminator": target.__class__.__table__.name,
                "parent_id": target.id,
                "operation": operation,
                "created_by_id": user_id,
                "data": prepared,
            }
        )
    )


@event.listens_for(HasAuditLog, "after_insert", propagate=True)
def receive_after_insert(mapper, connection, target):
    add_auditlog_entry(mapper, connection, target, "INSERT")


@event.listens_for(HasAuditLog, "after_update", propagate=True)
def receive_after_update(mapper, connection, target):
    add_auditlog_entry(mapper, connection, target, "UPDATE")


@event.listens_for(HasAuditLog, "after_delete", propagate=True)
def receive_after_delete(mapper, connection, target):
    add_auditlog_entry(mapper, connection, target, "DELETE")
