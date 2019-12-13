import typing

from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings, Secret


class AppConfig:
    _config = Config(".env")

    # email configuration
    email_backend: str = _config(
        "EMAIL_BACKEND", default="starlette_core.mail.backends.smtp.EmailBackend"
    )
    email_default_from_address: str = _config("EMAIL_DEFAULT_FROM_ADDRESS", default="")
    email_default_from_name: str = _config("EMAIL_DEFAULT_FROM_NAME", default="")
    email_host: str = _config("EMAIL_HOST", default="")
    email_port: typing.Optional[int] = _config("EMAIL_PORT", cast=int, default=None)
    email_username: str = _config("EMAIL_USERNAME", default="")
    email_password: typing.Union[str, Secret] = _config(
        "EMAIL_PASSWORD", cast=Secret, default=""
    )
    email_use_tls: bool = _config("EMAIL_USE_TLS", cast=bool, default=False)
    email_timeout: typing.Optional[int] = _config(
        "EMAIL_TIMEOUT", cast=int, default=None
    )
    # templating configuration
    jinja2_extensions: typing.List[str] = _config(
        "JINJA2_EXTENSIONS", cast=CommaSeparatedStrings, default=[]
    )


config = AppConfig()
