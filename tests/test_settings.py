import calendar
import datetime
import os

import pytest

from rororo.settings import (
    from_env,
    immutable_settings,
    inject_settings,
    is_setting_key,
    setup_locale,
    setup_timezone,
)
from . import settings as settings_module


TEST_DEBUG = True
TEST_USER = "test-user"
_TEST_USER = "private-user"


def check_immutability(settings):
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


def test_from_env():
    assert from_env("USER") == os.getenv("USER")
    assert from_env("DOES_NOT_EXIST") is None
    assert from_env("DOES_NOT_EXIST", True) is True


def test_immutable_settings_from_dict():
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
    settings = immutable_settings(globals())

    assert settings["TEST_DEBUG"] is True
    assert settings["TEST_USER"] == "test-user"
    assert "_TEST_USER" not in settings
    assert "pytest" not in settings

    check_immutability(settings)


def test_immutable_settings_from_locals():
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
    settings = immutable_settings(settings_module)

    assert settings["DEBUG"] is True
    assert settings["USER"] == os.getenv("USER")
    assert "os" not in settings

    check_immutability(settings)


def test_immutable_settings_with_optionals():
    settings = immutable_settings(settings_module, DEBUG=False)
    assert settings["DEBUG"] is False
    assert settings["USER"] == os.getenv("USER")


def test_inject_settings_fail_silently():
    context = {}
    inject_settings("tests.settings_error", context, True)
    assert context == {}


def test_inject_settings_failed():
    context = {}
    with pytest.raises(NameError):
        inject_settings("tests.settings_error", context)
    assert context == {}


def test_inject_settings_from_dict():
    context = {"DEBUG": False}
    settings_dict = {"DEBUG": True, "_DEBUG": True}
    inject_settings(settings_dict, context)
    assert context["DEBUG"] is True
    assert "_DEBUG" not in context


def test_inject_settings_from_module():
    context = {"DEBUG": False}
    inject_settings(settings_module, context)
    assert context["DEBUG"] is True
    assert "os" not in context


def test_inject_settings_from_str():
    context = {"DEBUG": False}
    inject_settings("tests.settings", context)
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
    assert is_setting_key(key) is expected


def test_setup_locale():
    monday = calendar.day_abbr[0]
    first_weekday = calendar.firstweekday()

    setup_locale("uk_UA.UTF-8")
    assert calendar.day_abbr[0] != monday
    assert calendar.firstweekday() == first_weekday


def test_setup_locale_with_first_weekday():
    first_weekday = calendar.firstweekday()

    setup_locale("uk_UA.UTF-8", 1)
    assert calendar.firstweekday() == 1

    setup_locale("en_US.UTF-8", first_weekday)


def test_setup_timezone():
    setup_timezone("UTC")
    utc_now = datetime.datetime.now()

    setup_timezone("Europe/Kiev")
    kyiv_now = datetime.datetime.now()

    assert utc_now.hour != kyiv_now.hour


def test_setup_timezone_empty():
    previous = datetime.datetime.now()
    setup_timezone(None)
    assert previous.hour == datetime.datetime.now().hour


def test_setup_timezone_unknown():
    with pytest.raises(ValueError):
        setup_timezone("Unknown/Timezone")
