import typing

import typesystem
from typesystem.fields import FORMATS

from .database import Base
from .formats import DateFormat, DateTimeFormat, TimeFormat
from .typesystem import Decimal, Email, Float

FORMATS.update(
    {"date": DateFormat(), "datetime": DateTimeFormat(), "time": TimeFormat()}
)


class ModelSchemaGenerator:
    """
    A class that generates a schema from a sqlalchemy model

    TODO:
    - relationships
    """

    # the model class
    model: typing.Type[Base]

    # the list of field names to include from the model
    model_fields: typing.List[str] = []

    # base set of mapped fields
    # fields will only be added if they are not already defined
    fields: typing.Dict[str, typesystem.Field] = {}

    # a dict of mapped sqlalchemy column type class names
    # and the class to validate in typesystem
    type_mapping = {
        "BigInteger": typesystem.Integer,
        "Boolean": typesystem.Boolean,
        "Date": typesystem.Date,
        "DateTime": typesystem.DateTime,
        "Float": Float,
        "Integer": typesystem.Integer,
        "Numeric": Decimal,
        "SmallInteger": typesystem.Integer,
        "String": typesystem.String,
        "Text": typesystem.Text,
        "Time": typesystem.Time,
        "Unicode": typesystem.String,
        "UnicodeText": typesystem.Text,
        "EmailType": Email,
    }

    def __new__(cls) -> "ModelSchemaGenerator":
        # loop over the class attrs and add to the fields dict
        # any that are and instance of `typesystem.Field`
        for key in dir(cls):
            if isinstance(getattr(cls, key), typesystem.Field):
                cls.fields[key] = getattr(cls, key)

        # add model fields
        cls.prepare_fields()

        # return our class
        return super().__new__(cls)

    @classmethod
    def prepare_fields(cls) -> None:
        """
        Iterate over `cls.model_fields` for each add
        a `typesystem.Field` relating to that field name in the
        declarative model `cls.model`.
        """

        # make sure the model inherits `starlette_core.database.Base`
        assert issubclass(cls.model, Base)

        # get the mapped table
        table = cls.model.__table__  # type: ignore

        # loop each field in model_fields and
        # create a schema field for it if it's
        # not already defined
        for field in cls.model_fields:

            # if its already defined do nothing
            if field in cls.fields:
                continue

            # otherwise add the field to the schema's fields
            if field in table.columns:
                # get the column and its type from sqlalchemy
                column = table.columns[field]
                column_type_class = column.type.__class__.__name__

                # create a new field
                new_field = cls.type_mapping[column_type_class]

                # get the fields defaults by mapping attributes from sqlalchemy
                field_kwargs = {"allow_null": column.nullable}

                if column_type_class in ["String", "Text", "Unicode", "UnicodeText"]:
                    field_kwargs["allow_blank"] = column.nullable
                    field_kwargs["max_length"] = column.type.length

                if column_type_class == "SmallInteger":
                    field_kwargs["minimum"] = -32768
                    field_kwargs["maximum"] = 32767

                if column_type_class == "Integer":
                    field_kwargs["minimum"] = -2147483648
                    field_kwargs["maximum"] = 2147483647

                if column_type_class == "BigInteger":
                    field_kwargs["minimum"] = -9223372036854775808
                    field_kwargs["maximum"] = 9223372036854775807

                if column_type_class == "Numeric":
                    if column.type.scale:
                        scale = "0" * column.type.scale
                        field_kwargs["precision"] = f"0.{scale}"

                cls.fields[field] = new_field(**field_kwargs)

    @classmethod
    def data_to_model(cls, data: typing.Dict, model_instance: typing.Any):
        """
        Loops over the items in `data` and sets an attr on `model_instance`
        to the value in `data`. But only if it exists.
        """

        for key in data.keys():
            if hasattr(model_instance, key):
                setattr(model_instance, key, getattr(data, key))
        return model_instance

    @classmethod
    def schema(cls) -> typing.Type[typesystem.Schema]:
        return type(str("ModelSchema"), (typesystem.Schema,), cls.fields)
