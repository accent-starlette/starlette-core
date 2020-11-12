from starlette.applications import Starlette
from starlette.authentication import AuthCredentials, AuthenticationBackend, SimpleUser
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette_core.database import Database, DatabaseURL

from . import models, routes

DEBUG = False


class DummyAuthBackend(AuthenticationBackend):
    async def authenticate(self, request):
        return AuthCredentials(["authenticated"]), SimpleUser("John Smith")


url = DatabaseURL("sqlite:///:memory:")
db = Database(url)

async def startup():
    await db.create_all()
    await models.DemoModel(name="Something").save()

async def shutdown():
    await db.drop_all()

# create app
app = Starlette(debug=DEBUG, on_startup=[startup], on_shutdown=[shutdown])

app.add_middleware(AuthenticationMiddleware, backend=DummyAuthBackend())
app.add_middleware(SessionMiddleware, secret_key="secret")

# mount routes
app.add_route(path="/", route=routes.homepage)
