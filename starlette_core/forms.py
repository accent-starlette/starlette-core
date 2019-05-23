import typing

import typesystem


class Form(typesystem.forms.Form):
    pass


class Jinja2Forms(typesystem.forms.Jinja2Forms):
    def Form(
        self,
        schema: typing.Type[typesystem.schemas.Schema],
        *,
        values: dict = None,
        errors: typesystem.base.ValidationError = None,
    ) -> Form:  # type: ignore
        return Form(env=self.env, schema=schema, values=values, errors=errors)
