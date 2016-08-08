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

from distutils.util import strtobool
from importlib import import_module
from locale import LC_ALL, setlocale
from logging.config import dictConfig as setup_logging  # noqa


def from_env(key, default=None):
    """Shortcut for safely reading environment variable.

    :param key: Environment var key.
    :type key: str
    :param default:
        Return default value if environment var not found by given key. By
        default: ``None``
    :type default: mixed
    :rtype: mixed
    """
    return os.environ.get(key, default)


def immutable_settings(defaults, **optionals):
    r"""Initialize and return immutable Settings dictionary.

    Settings dictionary allows you to setup settings values from multiple
    sources and make sure that values cannot be changed, updated by anyone else
    after initialization. This helps keep things clear and not worry about
    hidden settings change somewhere around your web application.

    :param defaults:
       Read settings values from module or dict-like instance.
    :type defaults: module or dict
    :param \*\*optionals:
        Update base settings with optional values.

        In common additional values shouldn't be passed, if settings values
        already populated from local settings or environment. But in case
        of using application factories this makes sense::

            from . import settings

            def create_app(**options):
                app = ...
                app.settings = Settings(settings, **options)
                return app

        And yes each additional key overwrite default setting value.
    :type \*\*optionals: dict
    :rtype: types.MappingProxyType
    """
    settings = {key: value for key, value in iter_settings(defaults)}
    for key, value in iter_settings(optionals):
        settings[key] = value
    return types.MappingProxyType(settings)


def inject_settings(mixed, context, fail_silently=False):
    """Inject settings values to given context.

    :param mixed:
        Settings could read from Python path, Python module or dict-like
        instance.
    :type mixed: str, module or dict
    :param context: Context should support dict-like item assingment.
    :type context: dict
    :param fail_silently:
        When enabled and reading settings from Python path ignore errors if
        given Python path couldn't be loaded.
    :type fail_silently: boolean
    :rtype: None
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


def is_setting_key(key):
    """Check whether given key is valid setting key or not.

    Only public uppercase constants are valid settings keys, all other keys
    are invalid and shouldn't present in Settings dict.

    Valid settings keys
    -------------------

    ::

        DEBUG
        SECRET_KEY

    Invalid settings keys
    ---------------------

    ::

        _PRIVATE_SECRET_KEY
        camelCasedSetting
        rel
        secret_key

    :param key: Key to check.
    :type key: str
    :rtype: bool
    """
    return key.isupper() and key[0] != '_'


def iter_settings(mixed):
    """Iterate over settings values from settings module or dict-like instance.

    :param mixed: Settings instance to iterate.
    :type mixed: module or dict
    :rtype: generator
    """
    if isinstance(mixed, types.ModuleType):
        for attr in dir(mixed):
            if not is_setting_key(attr):
                continue
            yield (attr, getattr(mixed, attr))
    else:
        yield from filter(lambda item: is_setting_key(item[0]), mixed.items())


def setup_locale(locale, first_weekday=None):
    """Setup locale for backend application.

    :param locale: Locale to use.
    :type locale: str
    :param first_weekday:
        Weekday for start week. 0 for Monday, 6 for Sunday. By default: None
    :type first_weekday: bool
    :rtype: bool
    """
    if first_weekday is not None:
        calendar.setfirstweekday(first_weekday)
    return setlocale(LC_ALL, locale)


def setup_timezone(timezone):
    """Setup timezone for backend application.

    :param timezone: Timezone to use, e.g. "UTC", "Europe/Kiev".
    :type timezone: str
    :rtype: None
    """
    if timezone and hasattr(time, 'tzset'):
        tz_root = '/usr/share/zoneinfo'
        tz_filename = os.path.join(tz_root, *(timezone.split('/')))

        if os.path.exists(tz_root) and not os.path.exists(tz_filename):
            raise ValueError('Incorrect timezone value: {0}'.format(timezone))

        os.environ['TZ'] = timezone
        time.tzset()


def to_bool(value):
    """Convert string or other Python value to boolean.

    Rationalle
    ==========

    Passing flags is one of the most used cases of using environment vars and
    as values are strings we need easy way to convert them to something
    suitable with Python for later usage.

    And when ``int`` or ``float`` values should be converted without extra
    work, ``bool('0') => True``. So in case of expecting boolean flag from
    environment just use this function for all good things.

    :param value: String or other value.
    :type: mixed
    :rtype: bool
    """
    return bool(strtobool(value) if isinstance(value, str) else value)
