import typing

import typesystem

from .fields import ModelChoice


class Form(typesystem.forms.Form):
    def template_for_field(self, field: typesystem.fields.Field) -> str:
        template = super().template_for_field(field)
        if isinstance(field, ModelChoice):
            return "forms/select.html"
        return template


class Jinja2Forms(typesystem.forms.Jinja2Forms):
    def Form(
        self,
        schema: typing.Type[typesystem.schemas.Schema],
        *,
        values: dict = None,
        errors: typesystem.base.ValidationError = None,
    ) -> Form:  # type: ignore
        return Form(env=self.env, schema=schema, values=values, errors=errors)
