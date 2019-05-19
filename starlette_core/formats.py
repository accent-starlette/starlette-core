import typing

from typesystem import formats


class TimeFormat(formats.TimeFormat):
    def serialize(self, obj: typing.Any) -> typing.Union[str, None]:
        return obj.isoformat() if obj is not None else None


class DateFormat(formats.DateFormat):
    def serialize(self, obj: typing.Any) -> typing.Union[str, None]:
        return obj.isoformat() if obj is not None else None


class DateTimeFormat(formats.DateTimeFormat):
    def serialize(self, obj: typing.Any) -> typing.Union[str, None]:
        if obj is None:
            return None
        value = obj.isoformat()
        if value.endswith("+00:00"):
            value = value[:-6] + "Z"
        return value
