import typing
from email.message import EmailMessage

import aiosmtplib
from starlette.datastructures import Secret

from starlette_core.config import config

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

    @property
    def connection_class(self):
        return aiosmtplib.SMTP

    async def open(self):
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
                hostname=self.host, port=self.port, **connection_params
            )

            await self.connection.connect()

            if self.use_tls:
                await self.connection.starttls()

            if self.username and self.password:
                await self.connection.login(self.username, str(self.password))

            return True
        except OSError:
            if not self.fail_silently:
                raise

    async def close(self):
        """Close the connection to the email server."""

        if self.connection is None:
            return

        try:
            try:
                await self.connection.quit()
            except:
                if self.fail_silently:
                    return
                raise
        finally:
            self.connection = None

    async def send_messages(self, email_messages: typing.List[EmailMessage]) -> int:
        """
        Send one or more EmailMessage objects and return the number of email
        messages sent.
        """

        if not email_messages:
            return 0

        new_conn_created = await self.open()
        if not self.connection or new_conn_created is None:
            # We failed silently on open(). Trying to send would be pointless.
            return 0
        num_sent = 0
        for message in email_messages:
            sent = await self._send(message)
            if sent:
                num_sent += 1
        if new_conn_created:
            await self.close()

        return num_sent

    async def _send(self, email_message: EmailMessage):
        """A helper method that does the actual sending."""

        if not self.connection:
            # We failed silently on open(). Trying to send would be pointless.
            return False

        try:
            await self.connection.send_message(email_message)
        except:
            if not self.fail_silently:
                raise
            return False

        return True
