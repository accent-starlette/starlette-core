import typing

import typesystem
from typesystem.unique import Uniqueness


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


class IntegerChoice(typesystem.Choice):
    """ A choice field that allows its choices to be integers

    Example:

        choices = [(1, "One"), (2, "Two")]
    """

    errors = {
        "null": "May not be null.",
        "required": "This field is required.",
        "choice": "Not a valid choice.",
        "integer": "Not a valid integer",
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
        if isinstance(value, str) and value.isdigit():
            value = int(value)
        elif value == "":
            value = None
        elif not isinstance(value, int):
            raise self.validation_error("integer")

        if value is None and self.allow_null:
            return None
        elif value is None:
            raise self.validation_error("null")
        elif value and isinstance(value, str) and not value.isdigit():
            raise self.validation_error("choice")
        elif value and not isinstance(value, int):
            raise self.validation_error("choice")
        elif value not in Uniqueness([key for key, value in self.choices]):
            raise self.validation_error("choice")

        return value
