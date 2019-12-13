# Configuration

There are several parts of the package that require config options like email. 

Configuration should be stored in environment variables, or in a ".env" file that is not committed to source control.

## Email

These are for the smtp email backend.

```bash
EMAIL_BACKEND=starlette_core.mail.backends.smtp.EmailBackend  # default
EMAIL_DEFAULT_FROM_ADDRESS=barry@example.com
EMAIL_DEFAULT_FROM_NAME=Barry
EMAIL_HOST=mail
EMAIL_PORT=537
EMAIL_USERNAME=username
EMAIL_PASSWORD=password
EMAIL_USE_TLS=True
EMAIL_TIMEOUT=5
```

If you don't want to set these as environment variables you can also define them in code.

```python
from starlette.applications import Starlette
from starlette_core import config

config.email_backend = ...
config.email_default_from_address = ...
config.email_default_from_name = ...
config.email_host = ...
config.email_port = ...
config.email_username = ...
config.email_password = ...
config.email_use_tls = ...
config.email_timeout = ...

app = Starlette()
```

## Jinja2 Extensions

These are added to the template configuration.

```bash
JINJA2_EXTENSIONS=jinja2.ext.i18n, myproject.ext.foo
```

If you don't want to set these as environment variables you can also define them in code.

```python
from starlette.applications import Starlette
from starlette_core import config

config.jinja2_extensions = ["jinja2.ext.i18n", "myproject.ext.foo"]

app = Starlette()
```