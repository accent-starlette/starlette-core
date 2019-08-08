from html import unescape
from os.path import dirname, join, realpath

import jinja2
from starlette.applications import Starlette
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse
from starlette.testclient import TestClient

from starlette_core.messages import message
from starlette_core.templating import Jinja2Templates

templates_directory = join(dirname(realpath(__file__)), "templates")
templates = Jinja2Templates(loader=jinja2.FileSystemLoader(templates_directory))


def add_message(request):
    message(request, "Hello World")
    return RedirectResponse("/view", status_code=302)


def view_message(request):
    context = {"request": request}
    return templates.TemplateResponse("message.html", context)


def create_app():
    app = Starlette()
    app.add_route("/add", add_message)
    app.add_route("/view", view_message)
    app.add_middleware(SessionMiddleware, secret_key="secret")
    return app


def test_message_in_template():
    with TestClient(create_app()) as client:
        # a message should live between requests
        response = client.get("/add")
        assert """<p class="default">Hello World</p>""" in unescape(response.text)

        response = client.get("/view")
        # once a message is consumed it should be removed
        assert """<p class="default">Hello World</p>""" not in unescape(response.text)
