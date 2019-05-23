import decimal
import typing

import typesystem
from sqlalchemy import orm
from typesystem.unique import Uniqueness


class Decimal(typesystem.Decimal):
    def serialize(self, obj: typing.Any) -> typing.Any:
        return decimal.Decimal(obj) if obj is not None else None


class Email(typesystem.String):
    """ A field that validates an email """

    custom_errors = {"pattern": "Must be a valid email."}

    def __init__(self, **kwargs: typing.Any) -> None:
        kwargs.setdefault(
            "pattern", r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        )
        kwargs.setdefault("format", "email")
        self.errors.update(self.custom_errors)
        super().__init__(**kwargs)


class Float(typesystem.Float):
    def serialize(self, obj: typing.Any) -> typing.Any:
        return float(obj) if obj is not None else None


class ModelChoice(typesystem.Choice):
    def __init__(self, *, queryset: orm.Query, **kwargs: typing.Any) -> None:
        super().__init__(**kwargs)
        self.queryset = queryset
        self.choices = [(o.id, str(o)) for o in self.queryset]

    @property
    def choices(self):
        return self.__choices

    @choices.setter
    def choices(self, choices):
        self.__choices = choices

    def validate(self, value: typing.Any, *, strict: bool = False) -> typing.Any:
        if value is None and self.allow_null:
            return None
        elif value == "" and self.allow_null:
            return None
        elif value == "":
            raise self.validation_error("required")
        elif value is None:
            raise self.validation_error("null")

        try:
            instance = self.queryset.filter_by(id=value).one()
            return instance.id
        except orm.exc.NoResultFound:
            raise self.validation_error("choice")
