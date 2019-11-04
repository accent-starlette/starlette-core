import smtplib
import threading
import typing
from email.message import EmailMessage

from starlette.datastructures import Secret

from ...config import config
from .base import BaseEmailBackend


class EmailBackend(BaseEmailBackend):
    """ A wrapper that manages the SMTP network connection. """

    def __init__(
        self,
        host: typing.Optional[str] = None,
        port: typing.Optional[int] = None,
        username: typing.Optional[str] = None,
        password: typing.Optional[Secret] = None,
        use_tls: typing.Optional[bool] = None,
        fail_silently: bool = False,
        timeout: typing.Optional[int] = None,
        **kwargs: typing.Any
    ) -> None:
        super().__init__(fail_silently=fail_silently)
        self.host = host or config.email_host
        self.port = port or config.email_port
        self.username = username or config.email_username
        self.password = password or config.email_password
        self.use_tls = use_tls or config.email_use_tls
        self.timeout = timeout or config.email_timeout
        self.connection = None
        self._lock = threading.RLock()

    @property
    def connection_class(self):
        return smtplib.SMTP

    def open(self):
        """
        Ensure an open connection to the email server. Return whether or not a
        new connection was required (True or False) or None if an exception
        passed silently.
        """

        if self.connection:
            # Nothing to do if the connection is already open.
            return False

        connection_params = {}
        if self.timeout is not None:
            connection_params["timeout"] = self.timeout

        try:
            self.connection = self.connection_class(
                self.host, self.port, **connection_params
            )

            if self.use_tls:
                self.connection.starttls()

            if self.username and self.password:
                self.connection.login(self.username, str(self.password))

            return True
        except OSError:
            if not self.fail_silently:
                raise

    def close(self):
        """Close the connection to the email server."""

        if self.connection is None:
            return

        try:
            try:
                self.connection.quit()
            except smtplib.SMTPServerDisconnected:
                # This happens when calling quit() on a TLS connection
                # sometimes, or when the connection was already disconnected
                # by the server.
                self.connection.close()
            except smtplib.SMTPException:
                if self.fail_silently:
                    return
                raise
        finally:
            self.connection = None

    def send_messages(self, email_messages: typing.List[EmailMessage]) -> int:
        """
        Send one or more EmailMessage objects and return the number of email
        messages sent.
        """

        if not email_messages:
            return 0

        with self._lock:
            new_conn_created = self.open()
            if not self.connection or new_conn_created is None:
                # We failed silently on open(). Trying to send would be pointless.
                return 0
            num_sent = 0
            for message in email_messages:
                sent = self._send(message)
                if sent:
                    num_sent += 1
            if new_conn_created:
                self.close()

        return num_sent

    def _send(self, email_message: EmailMessage):
        """A helper method that does the actual sending."""

        if not self.connection:
            # We failed silently on open(). Trying to send would be pointless.
            return False

        try:
            self.connection.send_message(email_message)
        except smtplib.SMTPException:
            if not self.fail_silently:
                raise
            return False

        return True
