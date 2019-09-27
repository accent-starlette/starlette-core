from contextvars import ContextVar
from uuid import uuid4

from starlette.types import ASGIApp, Receive, Scope, Send

_request_id_ctx_var: ContextVar[str] = ContextVar(
    "request_id", default=None  # type: ignore
)


_request_ctx_var: ContextVar[Scope] = ContextVar(
    "request", default=None  # type: ignore
)


def get_request_id() -> str:
    return _request_id_ctx_var.get()


def get_request() -> Scope:
    return _request_ctx_var.get()


class CurrentRequestMiddleware:
    """
    Sets the _request_ctx_var to the request.

    Usage:
        from starlette_core.middleware import get_request
        get_request()
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        local_scope = _request_ctx_var.set(scope)

        response = await self.app(scope, receive, send)

        _request_ctx_var.reset(local_scope)

        return response


class DatabaseMiddleware:
    """
    Sets the _request_id_ctx_var to a new uuid. This inturn is used
    by the `starlette_core.database.Session` object to isolate the
    session between requests.

    Usage:
        from starlette_core.middleware import get_request_id
        get_request_id()
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        request_id = _request_id_ctx_var.set(str(uuid4()))

        response = await self.app(scope, receive, send)

        from .database import Session

        if Session.registry.has():
            Session.remove()

        _request_id_ctx_var.reset(request_id)

        return response
