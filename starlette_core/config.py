from starlette.datastructures import Secret
import typing


class AppConfig:
    email_default_from_address: str = None
    email_default_from_name: str = None
    email_host: str = None
    email_port: int = None
    email_username: str = None
    email_password: typing.Union[str, Secret] = None
    email_use_tls: bool = False


config = AppConfig()
