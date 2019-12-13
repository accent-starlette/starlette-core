import typing

from starlette import templating
from starlette.datastructures import QueryParams
from wtforms import fields, form

from .config import config
from .messages import get_messages

try:
    import jinja2
except ImportError:  # pragma: nocover
    jinja2 = None  # type: ignore


class Jinja2Templates(templating.Jinja2Templates):
    def __init__(self, loader: "jinja2.BaseLoader") -> None:
        assert jinja2 is not None, "jinja2 must be installed to use Jinja2Templates"
        self.env = self.get_environment(loader)

    def get_environment(self, loader: "jinja2.BaseLoader") -> "jinja2.Environment":
        @jinja2.contextfunction
        def get_request_messages(context: dict):
            request = context["request"]
            return get_messages(request)

        def is_multipart(form: form.Form) -> bool:
            return any(isinstance(field, fields.FileField) for field in form)

        @jinja2.contextfunction
        def url_for(context: dict, name: str, **path_params: typing.Any) -> str:
            request = context["request"]
            return request.url_for(name, **path_params)

        def url_params_update(init: QueryParams, **new: typing.Any) -> QueryParams:
            values = dict(init)
            values.update(new)
            return QueryParams(**values)

        env = jinja2.Environment(
            extensions=list(config.jinja2_extensions), loader=loader, autoescape=True
        )

        env.globals["get_messages"] = get_request_messages
        env.globals["is_multipart"] = is_multipart
        env.globals["url_for"] = url_for
        env.globals["url_params_update"] = url_params_update

        return env
