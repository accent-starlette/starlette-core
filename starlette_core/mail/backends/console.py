import sys
import typing
from email.message import EmailMessage

from .base import BaseEmailBackend


class EmailBackend(BaseEmailBackend):
    """ A wrapper that sends email to the console. """

    def __init__(self, fail_silently: bool = False, **kwargs: typing.Any) -> None:
        super().__init__(fail_silently=fail_silently)
        self.stream = kwargs.pop("stream", sys.stdout)

    async def write_message(self, message):
        msg_data = message.as_bytes()
        charset = (
            message.get_charset().get_output_charset()
            if message.get_charset()
            else "utf-8"
        )
        msg_data = msg_data.decode(charset)
        self.stream.write("%s\n" % msg_data)
        self.stream.write("-" * 79)
        self.stream.write("\n")

    async def send_messages(self, email_messages: typing.List[EmailMessage]) -> int:
        """ Write all messages to the stream in a thread-safe way. """

        if not email_messages:
            return 0
        msg_count = 0
        try:
            stream_created = await self.open()
            for message in email_messages:
                await self.write_message(message)
                self.stream.flush()
                msg_count += 1
            if stream_created:
                await self.close()
        except Exception:
            if not self.fail_silently:
                raise
        return msg_count
