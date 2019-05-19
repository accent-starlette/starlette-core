import datetime
import decimal

import sqlalchemy as sa
import typesystem

from starlette_core.database import Base
from starlette_core.schemas import ModelSchemaGenerator


class MyTestModel(Base):
    bigint = sa.Column(sa.BigInteger)
    boolean = sa.Column(sa.Boolean)
    date = sa.Column(sa.Date)
    datetime = sa.Column(sa.DateTime)
    float = sa.Column(sa.Float)
    integer = sa.Column(sa.Integer)
    numeric = sa.Column(sa.Numeric(5, 2))
    smallint = sa.Column(sa.SmallInteger)
    string = sa.Column(sa.String(50))
    text = sa.Column(sa.Text)
    time = sa.Column(sa.Time)
    unicode = sa.Column(sa.Unicode(50))
    unicodetext = sa.Column(sa.UnicodeText)


class MyTestModelSchema(ModelSchemaGenerator):
    model = MyTestModel
    model_fields = [
        "bigint",
        "boolean",
        "date",
        "datetime",
        "float",
        "integer",
        "numeric",
        "smallint",
        "string",
        "text",
        "unicode",
        "unicodetext",
        "time",
    ]

    predefined = typesystem.Integer(allow_null=True)


def test_schema_generator():
    validated_data, errors = MyTestModelSchema.schema().validate_or_error({})

    assert validated_data is not None
    assert errors is None

    model = MyTestModel()
    model = MyTestModelSchema.data_to_model(validated_data, model)
    model.save()

    validated_data, errors = MyTestModelSchema.schema().validate_or_error(
        {
            "bigint": 1000000000,
            "boolean": True,
            "date": datetime.datetime.utcnow().date(),
            "datetime": datetime.datetime.utcnow(),
            "float": float("1000.00010"),
            "integer": 10000,
            "numeric": decimal.Decimal("100.001"),
            "smallint": 100,
            "string": "hello",
            "text": "some text\nanother line",
            "unicode": "I ♥ Python",
            "unicodetext": "I still ♥ Python",
            "time": datetime.datetime.utcnow().time(),
            # custom
            "predefined": 1,
        }
    )

    assert validated_data is not None
    assert errors is None

    model = MyTestModel()
    model = MyTestModelSchema.data_to_model(validated_data, model)
    model.save()
