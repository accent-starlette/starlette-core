# Email

Email support is provided by default. It is built in a way of using backends which are
used to process the email.

## Sending the email

The `send_message` takes an instance of `email.message.EmailMessage`. [See docs.](https://docs.python.org/3/library/email.examples.html).

To send an email:

```python
from email.message import EmailMessage
from starlette_core.mail import send_message

msg = EmailMessage()

msg["Subject"] = "Subject"
msg["From"] = "From <from@example.com>"
msg["To"] = "To <to@example.com>"

msg.set_content(
    """
    Dear To,

    This is the email contents.

    Thanks.
    """
)

send_message(msg)
```

## Backends

Details of the differend email backends are provided below.

### SMTP backend

The `starlette_core.mail.backends.smtp.EmailBackend` (which is the default). Will send 
an email using pythons base email modules.

This does require several default configuration options. [See docs](/configuration).

### Console backend

The `starlette_core.mail.backends.console.EmailBackend` can be used to simulate sending 
an email. All it does is prints the contents of the email to `sys.stdout`. This is useful
when developing locally.