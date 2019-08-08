import typing

from starlette.requests import Request


def message(request: Request, message: typing.Any, category: str = "default") -> None:
    if "_messages" not in request.session:
        request.session["_messages"] = []
    request.session["_messages"].append({"message": message, "category": category})


def get_messages(request: Request):
    return request.session.pop("_messages") if "_messages" in request.session else []
