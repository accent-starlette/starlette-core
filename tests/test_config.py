from starlette_core import config


def test_defaults():
    assert config.email_backend == "starlette_core.mail.backends.smtp.EmailBackend"
    assert config.email_default_from_address == ""
    assert config.email_default_from_name == ""
    assert config.email_host == ""
    assert config.email_port is None
    assert config.email_username == ""
    assert str(config.email_password) == ""
    assert config.email_use_tls is False
    assert config.email_timeout is None
    assert config.jinja2_extensions == []
