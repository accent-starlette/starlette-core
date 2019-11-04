import typing

from starlette.datastructures import Secret


class AppConfig:
    email_backend: str = "starlette_core.mail.backends.smtp.EmailBackend"
    email_default_from_address: str = ""
    email_default_from_name: str = ""
    email_host: str
    email_port: int
    email_username: str = ""
    email_password: typing.Union[str, Secret] = ""
    email_use_tls: bool = False
    email_timeout: typing.Optional[int] = None
    jinja2_extensions: typing.List[str] = []


config = AppConfig()
