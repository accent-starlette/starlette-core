from email.message import EmailMessage

from mock import call, patch

from starlette_core import config
from starlette_core.mail import send_message


def test_send_message():
    config.email_default_from_address = "foo@mail.com"
    config.email_default_from_name = "Foo"
    config.email_host = "mail"
    config.email_port = 25
    config.email_username = ""
    config.email_password = ""
    config.email_use_tls = False

    msg = EmailMessage()
    msg["Subject"] = "hello"
    msg["To"] = "bar@mail.com"
    msg.set_content("hello peeps")

    # called with correct creds
    with patch("smtplib.SMTP") as mock_smtp:
        send_message(msg)
        assert mock_smtp.call_args == call("mail", 25)

    # login called - empty details
    with patch("smtplib.SMTP") as mock_smtp:
        send_message(msg)
        instance = mock_smtp.return_value
        instance.login.assert_called_with("", "")

    config.email_username = "username"
    config.email_password = "password"

    # login called - with details
    with patch("smtplib.SMTP") as mock_smtp:
        send_message(msg)
        instance = mock_smtp.return_value
        instance.login.assert_called_with("username", "password")

    config.email_use_tls = True

    # use tls called
    with patch("smtplib.SMTP") as mock_smtp:
        send_message(msg)
        instance = mock_smtp.return_value
        assert 2 == instance.ehlo.call_count
        assert instance.starttls.called

    # message sent
    with patch("smtplib.SMTP") as mock_smtp:
        send_message(msg)
        instance = mock_smtp.return_value
        assert 1 == instance.send_message.call_count
