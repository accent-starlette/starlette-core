import smtplib

from email.message import EmailMessage
import email.utils

from .config import config


def send_message(msg: EmailMessage):
    """ Send an ``email.message.EmailMessage``. """

    if not msg.get('From'):
        msg['From'] = email.utils.formataddr(
            (config.email_default_from_name, config.email_default_from_address)
        )

    server = smtplib.SMTP(config.email_host, config.email_port)

    if config.email_use_tls:
        server.ehlo()
        server.starttls()
        server.ehlo()

    server.login(config.email_username, str(config.email_password))
    server.send_message(msg)
    server.close()
