import httpx
import pytest
from starlette.applications import Starlette
from starlette.responses import JSONResponse

from starlette_core.database import Session
from starlette_core.middleware import DatabaseMiddleware, get_request_id


def session_initialized(request):
    Session()
    has_session = get_request_id() in Session.registry.registry
    return JSONResponse({"has_session": has_session, "id": get_request_id()})


def session_not_initialized(request):
    has_session = get_request_id() in Session.registry.registry
    return JSONResponse({"has_session": has_session, "id": get_request_id()})


def create_app():
    app = Starlette()
    app.add_route("/session_initialized", session_initialized)
    app.add_route("/session_not_initialized", session_not_initialized)
    app.add_middleware(DatabaseMiddleware)
    return app


@pytest.mark.anyio
async def test_database_middleware(db):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=create_app()), base_url="https://testclient"
    ) as client:
        # by not initializing it doesnt break
        json = (await client.get("/session_not_initialized")).json()
        assert not json["has_session"]
        assert json["id"] is not None
        assert json["id"] not in Session.registry.registry

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=create_app()), base_url="https://testclient"
    ) as client:
        # sessions are removed after the request
        json = (await client.get("/session_initialized")).json()
        assert json["has_session"]
        assert json["id"] is not None
        assert json["id"] not in Session.registry.registry
