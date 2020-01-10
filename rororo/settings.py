"""
===============
rororo.settings
===============

Useful functions to work with application settings such as,

- Locale
- Logging
- Time zone

As well as provide attrib factory helper to read settings from environment to
use within Settings data structures.

"""

import calendar
import locale
import logging
import os
import time
import types
from importlib import import_module
from logging.config import dictConfig
from typing import (
    Any,
    Collection,
    Iterator,
    MutableMapping,
    Optional,
    overload,
    Tuple,
    Union,
)

import attr
from aiohttp import web

from .annotations import DictStrAny, Level, MappingStrAny, Settings, T
from .logger import default_logging_dict
from .utils import ensure_collection, to_bool


APP_SETTINGS_KEY = "settings"


@overload
def env_factory(name: str) -> Optional[str]:
    ...  # pragma: no cover


@overload
def env_factory(name: str, default: T) -> T:
    ...  # pragma: no cover


def env_factory(name: str, default: T = None) -> Union[Optional[str], T]:
    """Helper to read attribute value from environment.

    It is designed to use, when settings is implemented as ``@attr.dataclass``
    data structure and there is a need to read value from environment via
    :func:`os.getenv` function.

    This factory function helps to:

    1. Eliminate necessity of using ``lambda`` functions when mixing
       ``os.getenv`` with ``attr``, like:
       ``attr.Factory(lambda: os.getenv("USER"))``
    2. Exclude ``# type: ignore`` from settings data structures
    3. Convert ``str`` values from environment to required type

    Example belows demonstrates ``env_factory`` usage variants,

    .. code-block:: python

        import attr


        @attr.dataclass
        class Settings:
            # As ``os.getenv(key)`` returns ``Optional[str]`` you need
            # to provide default value for each non-optional env attribs
            user: str = env_factory("USER", "default-user")

            # Convert string value from environment to ``Path``
            user_path: Path = env_factory("USER_PATH", Path("~"))

            # Or to integer
            user_level: int = env_factory("USER_LEVEL", 1)

            # When default value is omit env attrib is **optional**
            sentry_dsn: Optional[str] = env_factory("SENTRY_DSN")

    """

    def getenv() -> Union[Optional[str], T]:
        value = os.getenv(name)
        if default is None:
            return value

        if value is None:
            return default

        expected_type = type(default)
        if isinstance(value, expected_type):
            return value

        try:
            if expected_type is bool:
                return to_bool(value)  # type: ignore
            return expected_type(value)  # type: ignore
        except (TypeError, ValueError):
            raise ValueError(
                f"Unable to convert {name} env var to {expected_type}."
            )

    return attr.Factory(getenv)


@attr.dataclass(frozen=True, slots=True)
class BaseSettings:
    """Base Settings data structure for configuring ``aiohttp.web`` apps.

    Provides common attribs, which covers most of settings requires for
    run and configure ``aiohttp.web`` app. In same time it is designed to be
    inherited and completed with missed values in application as,

    .. code-block:: python

        import attr
        from rororo.settings import BaseSettings, env_factory


        @attr.dataclass(frozen=True, slots=True)
        class Settings(BaseSettings):
            other_name: str = env_factory("OTHER_NAME", "other-value")

    """

    # Base aiohttp settings
    host: str = env_factory("AIOHTTP_HOST", "localhost")
    port: int = env_factory("AIOHTTP_PORT", 8080)

    # Base application settings
    debug: bool = env_factory("DEBUG", False)
    level: Level = env_factory("LEVEL", "dev")

    # Date & time settings
    time_zone: str = env_factory("TIME_ZONE", "UTC")

    # Locale settings
    first_weekday: int = env_factory("FIRST_WEEKDAY", 0)
    locale: str = env_factory("LOCALE", "en_US.UTF-8")

    # Sentry settings
    sentry_dsn: Optional[str] = env_factory("SENTRY_DSN")
    sentry_release: Optional[str] = env_factory("SENTRY_RELEASE")

    def apply(
        self,
        *,
        loggers: Collection[str] = None,
        remove_root_handlers: bool = False,
    ) -> None:
        """
        Apply settings by calling setup logging, locale & timezone functions.

        Should be called once on application lifecycle. Best way to do it, to
        call right after settings instantiation.

        When ``loggers`` is passed, setup default logging dict for given
        iterable and call setup logging function. When ``loggers`` is omit do
        nothing.
        """
        if loggers:
            setup_logging(
                default_logging_dict(*ensure_collection(loggers)),
                remove_root_handlers=remove_root_handlers,
            )

        setup_locale(self.locale, self.first_weekday)
        setup_timezone(self.time_zone)

    @property
    def is_dev(self) -> bool:
        return self.level == "dev"

    @property
    def is_prod(self) -> bool:
        return self.level == "prod"

    @property
    def is_staging(self) -> bool:
        return self.level == "staging"

    @property
    def is_test(self) -> bool:
        return self.level == "test"


def from_env(key: str, default: T = None) -> Union[str, Optional[T]]:
    """Shortcut for safely reading environment variable.

    .. deprecated:: 2.0
        Use :func:`os.getenv` instead. Will be removed in **3.0**.

    :param key: Environment var key.
    :param default:
        Return default value if environment var not found by given key. By
        default: ``None``
    """
    return os.getenv(key, default)


def immutable_settings(defaults: Settings, **optionals: Any) -> MappingStrAny:
    r"""Initialize and return immutable Settings dictionary.

    Settings dictionary allows you to setup settings values from multiple
    sources and make sure that values cannot be changed, updated by anyone else
    after initialization. This helps keep things clear and not worry about
    hidden settings change somewhere around your web application.

    .. deprecated:: 2.0
        Function deprecated in favor or using `attrs <https://www.attrs.org>`_
        or `dataclasses <https://docs.python.org/3/library/dataclasses.html>`_
        for declaring settings classes. Will be removed in **3.0**.

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


def inject_settings(
    mixed: Union[str, Settings],
    context: MutableMapping[str, Any],
    fail_silently: bool = False,
) -> None:
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
    return key.isupper() and key[0] != "_"


def iter_settings(mixed: Settings) -> Iterator[Tuple[str, Any]]:
    """Iterate over settings values from settings module or dict-like instance.

    :param mixed: Settings instance to iterate.
    """
    if isinstance(mixed, types.ModuleType):
        for item in dir(mixed):
            if not is_setting_key(item):
                continue
            yield (item, getattr(mixed, item))
    else:
        yield from filter(lambda item: is_setting_key(item[0]), mixed.items())


def setup_locale(
    lc_all: str,
    first_weekday: int = None,
    *,
    lc_collate: str = None,
    lc_ctype: str = None,
    lc_messages: str = None,
    lc_monetary: str = None,
    lc_numeric: str = None,
    lc_time: str = None,
) -> str:
    """Shortcut helper to setup locale for backend application.

    :param lc_all: Locale to use.
    :param first_weekday:
        Weekday for start week. 0 for Monday, 6 for Sunday. By default: None
    :param lc_collate: Collate locale to use. By default: ``<lc_all>``
    :param lc_ctype: Ctype locale to use. By default: ``<lc_all>``
    :param lc_messages: Messages locale to use. By default: ``<lc_all>``
    :param lc_monetary: Monetary locale to use. By default: ``<lc_all>``
    :param lc_numeric: Numeric locale to use. By default: ``<lc_all>``
    :param lc_time: Time locale to use. By default: ``<lc_all>``
    """
    if first_weekday is not None:
        calendar.setfirstweekday(first_weekday)

    locale.setlocale(locale.LC_COLLATE, lc_collate or lc_all)
    locale.setlocale(locale.LC_CTYPE, lc_ctype or lc_all)
    locale.setlocale(locale.LC_MESSAGES, lc_messages or lc_all)
    locale.setlocale(locale.LC_MONETARY, lc_monetary or lc_all)
    locale.setlocale(locale.LC_NUMERIC, lc_numeric or lc_all)
    locale.setlocale(locale.LC_TIME, lc_time or lc_all)

    return locale.setlocale(locale.LC_ALL, lc_all)


def setup_logging(
    config: DictStrAny, *, remove_root_handlers: bool = False
) -> None:
    """Wrapper around :func:`logging.config.dictConfig` function.

    In most cases it is not necessary to use an additional wrapper for setting
    up logging, but if your ``aiohttp.web`` application run as::

        python -m aiohttp.web api.app:create_app

    ``aiohttp`` `will setup
    <https://github.com/aio-libs/aiohttp/blob/v3.6.2/aiohttp/web.py#L494>`_
    logging via :func:`logging.basicConfig` call and it may result in
    duplicated logging messages. To avoid duplication, it is needed to remove
    ``logging.root`` handlers.

    :param remove_root_handlers:
        Remove ``logging.root`` handlers if any. By default: ``False``
    """
    if remove_root_handlers:
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
    return dictConfig(config)


def setup_settings(
    app: web.Application,
    settings: BaseSettings,
    *,
    loggers: Collection[str] = None,
    remove_root_handlers: bool = False,
) -> web.Application:
    """Shortcut for applying settings for given ``aiohttp.web`` app.

    After applying, put settings to :class:`aiohttp.web.Application` dict as
    ``"settings"`` key.
    """
    settings.apply(loggers=loggers, remove_root_handlers=remove_root_handlers)
    app[APP_SETTINGS_KEY] = settings
    return app


def setup_timezone(timezone: str) -> None:
    """Shortcut helper to configure timezone for backend application.

    :param timezone: Timezone to use, e.g. "UTC", "Europe/Kiev".
    """
    if timezone and hasattr(time, "tzset"):
        tz_root = "/usr/share/zoneinfo"
        tz_filename = os.path.join(tz_root, *(timezone.split("/")))

        if os.path.exists(tz_root) and not os.path.exists(tz_filename):
            raise ValueError("Incorrect timezone value: {0}".format(timezone))

        os.environ["TZ"] = timezone
        time.tzset()


# Make flake8 happy
(setup_logging, to_bool)
