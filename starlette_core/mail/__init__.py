import email.utils
import typing
from email.message import EmailMessage

from ..config import config
from ..utils import import_string
from .backends.base import BaseEmailBackend


def get_connection(
    backend: typing.Optional[str] = None,
    fail_silently: bool = False,
    **kwds: typing.Any
):
    """Load an email backend and return an instance of it.
    If backend is None (default), use config.email_backend.
    Both fail_silently and other keyword arguments are used in the
    constructor of the backend.
    """
    klass = import_string(backend or config.email_backend)
    return klass(fail_silently=fail_silently, **kwds)


def send_message(
    msg: EmailMessage,
    connection: typing.Optional[BaseEmailBackend] = None,
    fail_silently: bool = False,
):
    """ Send an ``email.message.EmailMessage``. """

    if not msg.get("From"):
        msg["From"] = email.utils.formataddr(
            (config.email_default_from_name, config.email_default_from_address)
        )

    connection = connection or get_connection(fail_silently=fail_silently)
    return connection.send_messages([msg])
