from starlette.middleware.base import BaseHTTPMiddleware

from .database import Session


class DatabaseMiddleware(BaseHTTPMiddleware):
    """
    Remove the current db session so it doesnt live between
    requests. This should be added after all middleware
    that requires db access have been added.
    """

    async def dispatch(self, request, call_next):
        response = await call_next(request)
        if Session.registry.has():
            Session.remove()
        return response
