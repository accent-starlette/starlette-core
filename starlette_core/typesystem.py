import decimal
import typing

import typesystem
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


class IntegerChoice(typesystem.Choice):
    """
    A choice field that allows its choices to be integers
    Example: choices = [(1, "One"), (2, "Two")]
    """

    errors = {
        "null": "May not be null.",
        "required": "This field is required.",
        "choice": "Not a valid choice.",
    }

    def __init__(
        self,
        *,
        choices: typing.Sequence[typing.Union[int, typing.Tuple[int, str]]] = None,
        **kwargs: typing.Any,
    ) -> None:
        super().__init__(**kwargs)
        self.choices = [
            (choice if isinstance(choice, (tuple, list)) else (choice, choice))
            for choice in choices or []
        ]
        assert all(len(choice) == 2 for choice in self.choices)

    def validate(self, value: typing.Any, *, strict: bool = False) -> typing.Any:
        if value is None and self.allow_null:
            return None
        if value == "" and self.allow_null and not strict:
            return None
        elif value == "":
            raise self.validation_error("required")
        elif value is None:
            raise self.validation_error("null")

        if isinstance(value, str) and value.isdigit() and not strict:
            value = int(value)

        if value not in Uniqueness([key for key, value in self.choices]):
            raise self.validation_error("choice")

        return value
