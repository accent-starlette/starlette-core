import typing

from .database import Base


def assert_model_field(
    cls: typing.Type[Base],
    name: str,
    type: typing.Any,
    nullable: bool = True,
    index: bool = False,
    unique: bool = False,
    length: int = None,
):
    """
    Test a sqlalchemy model field.

    :param cls: A model class derived from a `starlette_core.database.Base`
    :param name: The name of the field
    :param type: The expected type of the field ie `sqlalchemy.String`
    :param nullable: Is the field nullable, `True` or `False`
    :param index: Is the field index, `True` or `False`
    :param unique: Is the field unique, `True` or `False`
    :param length: The expected length of the field ie 255
    """

    assert issubclass(cls, Base)

    field = cls.__table__.columns[name]  # type: ignore

    assert isinstance(field.type, type)

    if nullable:
        assert field.nullable
    else:
        assert not field.nullable

    if index:
        assert field.index
    else:
        assert not field.index

    if unique:
        assert field.unique
    else:
        assert not field.unique

    if length:
        assert field.type.length == length


class DummyPostData(dict):
    def getlist(self, key):
        v = self[key]
        if not isinstance(v, (list, tuple)):
            v = [v]
        return v
