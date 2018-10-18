"""
===============
rororo.settings
===============

Immutable Settings dictionary and various utilities to read settings values
from environment.

Module helps you to prepare and read settings inside your web application.

"""

import calendar
import os
import time
import types
from importlib import import_module
from locale import LC_ALL, setlocale
from logging.config import dictConfig as setup_logging  # noqa: N813
from typing import Any, Iterator, MutableMapping, Optional, Tuple, Union

from .annotations import Settings, T
from .utils import to_bool


def from_env(key: str, default: T=None) -> Union[str, Optional[T]]:
    """Shortcut for safely reading environment variable.

    :param key: Environment var key.
    :param default:
        Return default value if environment var not found by given key. By
        default: ``None``
    """
    return os.getenv(key, default)


def immutable_settings(defaults: Settings,
                       **optionals: Any) -> types.MappingProxyType:
    r"""Initialize and return immutable Settings dictionary.

    Settings dictionary allows you to setup settings values from multiple
    sources and make sure that values cannot be changed, updated by anyone else
    after initialization. This helps keep things clear and not worry about
    hidden settings change somewhere around your web application.

    :param defaults:
       Read settings values from module or dict-like instance.
    :param \*\*optionals:
        Update base settings with optional values.

        In common additional values shouldn't be passed, if settings values
        already populated from local settings or environment. But in case
        of using application factories this makes sense::

            from . import settings

            def create_app(**options):
                app = ...
                app.settings = immutable_settings(settings, **options)
                return app

        And yes each additional key overwrite default setting value.
    """
    settings = {key: value for key, value in iter_settings(defaults)}
    for key, value in iter_settings(optionals):
        settings[key] = value
    return types.MappingProxyType(settings)


def inject_settings(mixed: Union[str, Settings],
                    context: MutableMapping[str, Any],
                    fail_silently: bool=False) -> None:
    """Inject settings values to given context.

    :param mixed:
        Settings can be a string (that it will be read from Python path),
        Python module or dict-like instance.
    :param context:
        Context to assign settings key values. It should support dict-like item
        assingment.
    :param fail_silently:
        When enabled and reading settings from Python path ignore errors if
        given Python path couldn't be loaded.
    """
    if isinstance(mixed, str):
        try:
            mixed = import_module(mixed)
        except Exception:
            if fail_silently:
                return
            raise

    for key, value in iter_settings(mixed):
        context[key] = value


def is_setting_key(key: str) -> bool:
    """Check whether given key is valid setting key or not.

    Only public uppercase constants are valid settings keys, all other keys
    are invalid and shouldn't present in Settings dict.

    **Valid settings keys**

    ::

        DEBUG
        SECRET_KEY

    **Invalid settings keys**

    ::

        _PRIVATE_SECRET_KEY
        camelCasedSetting
        rel
        secret_key

    :param key: Key to check.
    """
    return key.isupper() and key[0] != '_'


def iter_settings(mixed: Settings) -> Iterator[Tuple[str, Any]]:
    """Iterate over settings values from settings module or dict-like instance.

    :param mixed: Settings instance to iterate.
    """
    if isinstance(mixed, types.ModuleType):
        for attr in dir(mixed):
            if not is_setting_key(attr):
                continue
            yield (attr, getattr(mixed, attr))
    else:
        yield from filter(lambda item: is_setting_key(item[0]), mixed.items())


def setup_locale(locale: str, first_weekday: int=None) -> str:
    """Shortcut helper to setup locale for backend application.

    :param locale: Locale to use.
    :param first_weekday:
        Weekday for start week. 0 for Monday, 6 for Sunday. By default: None
    """
    if first_weekday is not None:
        calendar.setfirstweekday(first_weekday)
    return setlocale(LC_ALL, locale)


def setup_timezone(timezone: str) -> None:
    """Shortcut helper to configure timezone for backend application.

    :param timezone: Timezone to use, e.g. "UTC", "Europe/Kiev".
    """
    if timezone and hasattr(time, 'tzset'):
        tz_root = '/usr/share/zoneinfo'
        tz_filename = os.path.join(tz_root, *(timezone.split('/')))

        if os.path.exists(tz_root) and not os.path.exists(tz_filename):
            raise ValueError('Incorrect timezone value: {0}'.format(timezone))

        os.environ['TZ'] = timezone
        time.tzset()


# Make flake8 happy
(setup_logging, to_bool)
