from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.testclient import TestClient

from starlette_core.database import Session
from starlette_core.middleware import DatabaseMiddleware


def session_initialized(request):
    Session()
    return JSONResponse({"has_session": Session.registry.has()})


def session_not_initialized(request):
    return JSONResponse({"has_session": Session.registry.has()})


def create_app():
    app = Starlette()
    app.add_route("/session_initialized", session_initialized)
    app.add_route("/session_not_initialized", session_not_initialized)
    app.add_middleware(DatabaseMiddleware)
    return app


def test_database_middleware(db):
    # by not initializing it doesnt break
    with TestClient(create_app()) as client:
        response = client.get("/session_not_initialized")
        assert response.json() == {"has_session": False}
    assert not Session.registry.has()

    # sessions are removed after the request
    with TestClient(create_app()) as client:
        response = client.get("/session_initialized")
        assert response.json() == {"has_session": True}
    assert not Session.registry.has()
