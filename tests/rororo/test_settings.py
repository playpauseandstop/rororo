import calendar
import datetime
import logging
import os

import environ
import pytest
from aiohttp import web

from rororo.logger import default_logging_dict
from rororo.settings import (
    BaseSettings,
    from_env,
    immutable_settings,
    inject_settings,
    is_setting_key,
    setup_locale,
    setup_logging,
    setup_settings,
    setup_timezone,
)
from . import settings as settings_module


TEST_DEBUG = True
TEST_USER = "test-user"
_TEST_USER = "private-user"


def check_immutability(settings):
    """
    Check that all evutututability

    Args:
        settings: (todo): write your description
    """
    # Cannot update current value
    key = list(settings.keys())[0]
    with pytest.raises(TypeError):
        settings[key] = "new-value"

    # Cannot add new value
    assert "TEST_SETTING" not in settings
    with pytest.raises(TypeError):
        settings["TEST_SETTING"] = "test-value"

    # Cannot update values at all
    with pytest.raises(AttributeError):
        settings.update({key: "new-value", "TEST_SETTING": "test_value"})


def test_base_settings():
    """
    Determine environment settings.

    Args:
    """
    settings = BaseSettings.from_environ()
    assert settings.host == "localhost"
    assert settings.port == 8080
    assert settings.debug is False
    assert settings.level == "test"
    assert settings.time_zone == "UTC"
    assert settings.first_weekday == 0
    assert settings.locale == "en_US.UTF-8"
    assert settings.sentry_dsn is None
    assert settings.sentry_release is None


def test_base_settings_apply():
    """
    Sets the settings to the settings.

    Args:
    """
    BaseSettings.from_environ().apply()


def test_base_settings_apply_with_loggers():
    """
    Configure logging settings.

    Args:
    """
    BaseSettings.from_environ().apply(loggers=("aiohttp", "rororo"))


def test_base_settings_from_env(monkeypatch):
    """
    Sets the default settings are set the environment variables.

    Args:
        monkeypatch: (todo): write your description
    """
    monkeypatch.setenv("DEBUG", "yes")
    assert BaseSettings.from_environ().debug is True


def test_base_settings_from_env_kwargs():
    """
    Sets the environment variables to the settings.

    Args:
    """
    assert BaseSettings.from_environ({"DEBUG": "true"}).debug is True


def test_base_settings_from_kwargs():
    """
    Gets the settings of the settings file.

    Args:
    """
    assert BaseSettings(debug=True).debug is True


def test_base_settings_inheritance(monkeypatch):
    """
    Sets the environment settings.

    Args:
        monkeypatch: (todo): write your description
    """
    monkeypatch.setenv("USE_RORORO", "yes")

    @environ.config(prefix=None, frozen=True)
    class Settings(BaseSettings):
        use_rororo: bool = environ.bool_var(name="USE_RORORO", default=True)

    settings = Settings.from_environ()
    assert settings.debug is False
    assert settings.use_rororo is True


@pytest.mark.parametrize(
    "level, expected_is_test, expected_is_dev, expected_is_staging, "
    "expected_is_prod",
    (
        ("dev", False, True, False, False),
        ("test", True, False, False, False),
        ("prod", False, False, False, True),
        ("staging", False, False, True, False),
    ),
)
def test_base_settings_is_properties(
    monkeypatch,
    level,
    expected_is_test,
    expected_is_dev,
    expected_is_staging,
    expected_is_prod,
):
    """
    Check if the environment properties are set_is settings.

    Args:
        monkeypatch: (todo): write your description
        level: (todo): write your description
        expected_is_test: (str): write your description
        expected_is_dev: (str): write your description
        expected_is_staging: (todo): write your description
        expected_is_prod: (str): write your description
    """
    monkeypatch.setenv("LEVEL", level)
    settings = BaseSettings.from_environ()
    assert settings.is_test is expected_is_test
    assert settings.is_dev is expected_is_dev
    assert settings.is_staging is expected_is_staging
    assert settings.is_prod is expected_is_prod


def test_from_env():
    """
    Create a new test environment. env. env.

    Args:
    """
    assert from_env("USER") == os.getenv("USER")
    assert from_env("DOES_NOT_EXIST") is None
    assert from_env("DOES_NOT_EXIST", True) is True


def test_immutable_settings_from_dict():
    """
    Test if immutable settings are in settings.

    Args:
    """
    settings_dict = {
        "DEBUG": True,
        "USER": "test-user",
        "_USER": "private-user",
    }
    settings = immutable_settings(settings_dict)

    assert settings["DEBUG"] is True
    assert settings["USER"] == "test-user"
    assert "_USER" not in settings

    settings_dict.pop("USER")
    assert settings["USER"] == "test-user"

    check_immutability(settings)


def test_immutable_settings_from_globals():
    """
    Test if settings is_from settings.

    Args:
    """
    settings = immutable_settings(globals())

    assert settings["TEST_DEBUG"] is True
    assert settings["TEST_USER"] == "test-user"
    assert "_TEST_USER" not in settings
    assert "pytest" not in settings

    check_immutability(settings)


def test_immutable_settings_from_locals():
    """
    Test if immutable settings are in settings.

    Args:
    """
    DEBUG = True  # noqa: N806
    USER = "local-test-user"  # noqa: N806
    _USER = "private-user"  # noqa: N806
    not_a_setting = True

    settings = immutable_settings(locals())

    assert settings["DEBUG"] is True
    assert settings["USER"], "local-test-user"
    assert "_USER" not in settings
    assert "not_a_setting" not in settings

    del DEBUG, USER, _USER
    assert settings["USER"] == "local-test-user"

    check_immutability(settings)


def test_immutable_settings_from_module():
    """
    Test if an executable settings.

    Args:
    """
    settings = immutable_settings(settings_module)

    assert settings["DEBUG"] is True
    assert settings["USER"] == os.getenv("USER")
    assert "os" not in settings

    check_immutability(settings)


def test_immutable_settings_with_optionals():
    """
    Test if settings are valid settings.

    Args:
    """
    settings = immutable_settings(settings_module, DEBUG=False)
    assert settings["DEBUG"] is False
    assert settings["USER"] == os.getenv("USER")


def test_inject_settings_fail_silently():
    """
    Validate test_settings_settings inject_settings.

    Args:
    """
    context = {}
    inject_settings("tests.rororo.settings_error", context, True)
    assert context == {}


def test_inject_settings_failed():
    """
    Evaluate test test settings.

    Args:
    """
    context = {}
    with pytest.raises(NameError):
        inject_settings("tests.rororo.settings_error", context)
    assert context == {}


def test_inject_settings_from_dict():
    """
    Injects settings are inject.

    Args:
    """
    context = {"DEBUG": False}
    settings_dict = {"DEBUG": True, "_DEBUG": True}
    inject_settings(settings_dict, context)
    assert context["DEBUG"] is True
    assert "_DEBUG" not in context


def test_inject_settings_from_module():
    """
    Injects is_inject_inject_from_module

    Args:
    """
    context = {"DEBUG": False}
    inject_settings(settings_module, context)
    assert context["DEBUG"] is True
    assert "os" not in context


def test_inject_settings_from_str():
    """
    Loads inject_settings_from_from_settings.

    Args:
    """
    context = {"DEBUG": False}
    inject_settings("tests.rororo.settings", context)
    assert context["DEBUG"] is True
    assert "os" not in context


@pytest.mark.parametrize(
    "key, expected",
    (
        ("DEBUG", True),
        ("SECRET_KEY", True),
        ("_PRIVATE_USER", False),
        ("camelCase", False),
        ("secret_key", False),
    ),
)
def test_is_settings_key(key, expected):
    """
    Returns true if key is a valid expected key.

    Args:
        key: (str): write your description
        expected: (bool): write your description
    """
    assert is_setting_key(key) is expected


def test_setup_locale():
    """
    Test if the locale is the same.

    Args:
    """
    monday = calendar.day_abbr[0]
    first_weekday = calendar.firstweekday()

    setup_locale("uk_UA.UTF-8")
    assert calendar.day_abbr[0] != monday
    assert calendar.firstweekday() == first_weekday


def test_setup_locale_with_first_weekday():
    """
    Test if the first weekday in the first weekday.

    Args:
    """
    first_weekday = calendar.firstweekday()

    setup_locale("uk_UA.UTF-8", 1)
    assert calendar.firstweekday() == 1

    setup_locale("en_US.UTF-8", first_weekday)


def test_setup_logging():
    """
    Configure logging.

    Args:
    """
    setup_logging(default_logging_dict("rororo"))


@pytest.mark.parametrize("remove, expected", ((False, 2), (True, 0)))
def test_setup_logging_remove_root_handlers(remove, expected):
    """
    Removes root handlers.

    Args:
        remove: (bool): write your description
        expected: (todo): write your description
    """
    logging.basicConfig(level="INFO")
    assert len(logging.root.handlers) == 2

    setup_logging(default_logging_dict("rororo"), remove_root_handlers=remove)
    assert len(logging.root.handlers) == expected


def test_setup_settings():
    """
    Configure application settings.

    Args:
    """
    app = web.Application()
    assert "settings" not in app

    setup_settings(app, BaseSettings())
    assert "settings" in app


def test_setup_timezone():
    """
    Set the timezone timezone exists.

    Args:
    """
    setup_timezone("UTC")
    utc_now = datetime.datetime.now()

    setup_timezone("Europe/Kiev")
    kyiv_now = datetime.datetime.now()

    assert utc_now.hour != kyiv_now.hour


def test_setup_timezone_empty():
    """
    Test if the timezone is empty.

    Args:
    """
    previous = datetime.datetime.now()
    setup_timezone(None)
    assert previous.hour == datetime.datetime.now().hour


def test_setup_timezone_unknown():
    """
    Setup the time zonezone timezone.

    Args:
    """
    with pytest.raises(ValueError):
        setup_timezone("Unknown/Timezone")
