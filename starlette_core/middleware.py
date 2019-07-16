from starlette.types import Scope, Receive, Send


class DatabaseMiddleware:
    """
    Remove the current db session so it doesnt live between
    requests. This should be added after all middleware
    that requires db access have been added.
    """

    def __init__(self, app) -> None:
        self.app = app

    def cleanup_session(self):
        from .database import Session

        if Session.registry.has():
            Session.remove()

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        self.cleanup_session()
        await self.app(scope, receive, send)
