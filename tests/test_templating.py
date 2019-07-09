from os.path import dirname, join, realpath

import jinja2
from starlette import templating

from starlette_core.templating import Jinja2Templates

templates_directory = join(dirname(realpath(__file__)), "templates")
templates = Jinja2Templates(loader=jinja2.FileSystemLoader(templates_directory))


def test_inheritance():
    assert issubclass(Jinja2Templates, templating.Jinja2Templates)


def test_templates_loaded():
    assert templates.env.list_templates() == ["test1.html", "test2.html"]


def test_get_template():
    resp = templates.TemplateResponse("test1.html", {"request": {}})
    assert resp.template.name == "test1.html"


def test_env():
    assert isinstance(templates.env, jinja2.Environment)
    assert "url_params_update" in templates.env.globals
    assert "url_for" in templates.env.globals
