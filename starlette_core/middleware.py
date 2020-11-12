from contextvars import ContextVar

from starlette.types import ASGIApp, Receive, Scope, Send

_request_ctx_var: ContextVar[Scope] = ContextVar(
    "request", default=None  # type: ignore
)


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
