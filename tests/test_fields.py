import sqlalchemy as sa
from typesystem.base import ValidationError

from starlette_core.database import Base, Session
from starlette_core.fields import Email, ModelChoice


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


def test_model_choice(db):
    class Choice(Base):
        name = sa.Column(sa.String)

        def __str__(self):
            return self.name

    db.create_all()

    choice1 = Choice(name="Alpha")
    choice2 = Choice(name="Beta")
    choice3 = Choice(name="Charlie")
    session = Session()
    session.add_all([choice1, choice2, choice3])
    session.flush()

    qs = Choice.query.order_by("name")

    validator = ModelChoice(queryset=qs)
    assert validator.choices == [
        (choice1.id, str(choice1)),
        (choice2.id, str(choice2)),
        (choice3.id, str(choice3)),
    ]

    validator = ModelChoice(queryset=qs)
    value, error = validator.validate_or_error(None)
    assert error == ValidationError(text="May not be null.", code="null")

    validator = ModelChoice(queryset=qs)
    value, error = validator.validate_or_error("")
    assert error == ValidationError(text="This field is required.", code="required")

    validator = ModelChoice(queryset=qs, allow_null=True)
    value, error = validator.validate_or_error(None)
    assert error is None
    assert value is None

    validator = ModelChoice(queryset=qs, allow_null=True)
    value, error = validator.validate_or_error("")
    assert error is None
    assert value is None

    validator = ModelChoice(queryset=qs)
    value, error = validator.validate_or_error(choice1.id)
    assert error is None
    assert value == choice1.id

    validator = ModelChoice(queryset=qs)
    value, error = validator.validate_or_error(str(choice1.id))
    assert error is None
    assert value == choice1.id

    validator = ModelChoice(queryset=qs)
    value, error = validator.validate_or_error(-1)
    assert error == ValidationError(text="Not a valid choice.", code="choice")

    validator = ModelChoice(queryset=qs)
    value, error = validator.validate_or_error("-1")
    assert error == ValidationError(text="Not a valid choice.", code="choice")
