from typesystem.base import ValidationError

from starlette_core.typesystem import Email, IntegerChoice


def test_email():
    validator = Email()
    value, error = validator.validate_or_error("mail@somewhere.com")
    assert value == "mail@somewhere.com"

    validator = Email()
    value, error = validator.validate_or_error("mail@somewhere.")
    assert error == ValidationError(text="Must be a valid email.", code="pattern")

    validator = Email()
    value, error = validator.validate_or_error("mail@somewhere")
    assert error == ValidationError(text="Must be a valid email.", code="pattern")

    validator = Email()
    value, error = validator.validate_or_error("mail@")
    assert error == ValidationError(text="Must be a valid email.", code="pattern")

    validator = Email()
    value, error = validator.validate_or_error("mail")
    assert error == ValidationError(text="Must be a valid email.", code="pattern")


def test_integer_choice():
    validator = IntegerChoice(choices=[(1, "one"), (2, "two"), (3, "three")])
    value, error = validator.validate_or_error(None)
    assert error == ValidationError(text="May not be null.", code="null")

    validator = IntegerChoice(
        choices=[(1, "one"), (2, "two"), (3, "three")], allow_null=True
    )
    value, error = validator.validate_or_error(None)
    assert value is None
    assert error is None

    validator = IntegerChoice(choices=[(1, "one"), (2, "two"), (3, "three")])
    value, error = validator.validate_or_error("")
    assert error == ValidationError(text="This field is required.", code="required")

    validator = IntegerChoice(
        choices=[(1, "one"), (2, "two"), (3, "three")], allow_null=True
    )
    value, error = validator.validate_or_error("")
    assert value is None
    assert error is None

    validator = IntegerChoice(choices=[(1, "one"), (2, "two"), (3, "three")])
    value, error = validator.validate_or_error(4)
    assert error == ValidationError(text="Not a valid choice.", code="choice")

    validator = IntegerChoice(choices=[(1, "one"), (2, "two"), (3, "three")])
    value, error = validator.validate_or_error("4")
    assert error == ValidationError(text="Not a valid choice.", code="choice")

    validator = IntegerChoice(choices=[(1, "one"), (2, "two"), (3, "three")])
    value, error = validator.validate_or_error(1)
    assert value == 1

    validator = IntegerChoice(choices=[(1, "one"), (2, "two"), (3, "three")])
    value, error = validator.validate_or_error("1")
    assert value == 1

    validator = IntegerChoice(
        choices=[(None, "empty"), (1, "one"), (2, "two"), (3, "three")], allow_null=True
    )
    value, error = validator.validate_or_error("")
    assert value is None

    validator = IntegerChoice(
        choices=[(None, "empty"), (1, "one"), (2, "two"), (3, "three")], allow_null=True
    )
    value, error = validator.validate_or_error(None)
    assert value is None

    validator = IntegerChoice(choices=[1, 2, 3])
    value, error = validator.validate_or_error(2)
    assert value == 2

    validator = IntegerChoice(choices=[1, 2, 3])
    value, error = validator.validate_or_error("2")
    assert value == 2
