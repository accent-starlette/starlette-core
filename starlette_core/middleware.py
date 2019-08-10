import threading

from starlette.types import Receive, Scope, Send

request_local = threading.local()


def get_request():
    return getattr(request_local, "request", None)


class CurrentRequestMiddleware:
    """
    Populates the current request on a thread so that a model has
    access to the user outside of a view.
    """

    def __init__(self, app) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] in ("http", "websocket"):
            request_local.request = scope
        await self.app(scope, receive, send)


class DatabaseMiddleware:
    """
    Remove the current db session so it doesnt live between
    requests. This should be added after all middleware
    that requires db access have been added.
    """

    def __init__(self, app) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] in ("http", "websocket"):
            from .database import Session

            if Session.registry.has():
                Session.remove()
        await self.app(scope, receive, send)
