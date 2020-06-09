===================================
Setting up aiohttp.web applications
===================================

There are many ways on setting up ``aiohttp.web`` application, as well as there
are many ways of defining settings for them.

Most notable ways of managing settings are:

- Importing Python settings module and store it within
  :class:`aiohttp.web.Application` instance
- Reading settings from ``.yaml`` or ``.json`` file and store it again, in
  application instance

With that in mind, *rororo* insists of their way for setting up
``aiohttp.web`` application.

Step 1. Settings data structure
===============================

The main part of setup is Settings data structure backed by brilliant
`environ-config <https://environ-config.readthedocs.io/>`_ library. It stores
all settings values, as well as any other settings related data.

Example below illustrates how given Settings data structure may look like,

.. code-block:: python

    import environ


    @environ.config(prefix=None, frozen=True)
    class Settings:
        level: str
        debug: bool

*rororo* provides basic data structure, which covers most of common settings,
used withing ``aiohttp.web`` app. Given data structure available as:
:class:`rororo.settings.BaseSettings` and it contains next fields,

+--------------------+--------------------+----------------------------------------------------------------------------+
| Attrib             | Env var            | Description                                                                |
+====================+====================+============================================================================+
| ``host``           | ``AIOHTTP_HOST``   | Host, where ``aiohttp.web`` application expected to run. By default:       |
|                    |                    | ``"localhost"``                                                            |
+--------------------+--------------------+----------------------------------------------------------------------------+
| ``port``           | ``AIOHTTP_PORT``   | Port to run ``aiohttp.web`` application on. By default: ``8080``           |
+--------------------+--------------------+----------------------------------------------------------------------------+
| ``debug``          | ``DEBUG``          | When enabled, means that ``aiohttp.web`` application run in debug mode. By |
|                    |                    | default: ``False``                                                         |
+--------------------+--------------------+----------------------------------------------------------------------------+
| ``level``          | ``LEVEL``          | Application level (can be used as ``SENTRY_ENVIRONMENT``, for example).    |
|                    |                    | One of: ``"test"``, ``"dev"``, ``"staging"``, ``"prod"``. By default:      |
|                    |                    | ``"dev"``                                                                  |
+--------------------+--------------------+----------------------------------------------------------------------------+
| ``time_zone``      | ``TIME_ZONE``      | Time zone to use within application. By default: ``"UTC"``                 |
+--------------------+--------------------+----------------------------------------------------------------------------+
| ``first_weekday``  | ``FIRST_WEEKDAY``  | First weekday for calendar and other modules. By default: ``0`` (Monday)   |
+--------------------+--------------------+----------------------------------------------------------------------------+
| ``locale``         | ``LOCALE``         | Locale to use within app. By default: ``"en_US.UTF-8"``                    |
|                    |                    |                                                                            |
|                    |                    | .. note: For best results it is considered to better setup locale and      |
|                    |                    |    other ``LC_*`` env vars before running Python executable.               |
+--------------------+--------------------+----------------------------------------------------------------------------+
| ``sentry_dsn``     | ``SENTRY_DSN``     | Sentry DSN to use. By default: ``None``                                    |
+--------------------+--------------------+----------------------------------------------------------------------------+
| ``sentry_release`` | ``SENTRY_RELEASE`` | Sentry release. By default: ``None``                                       |
+--------------------+--------------------+----------------------------------------------------------------------------+

*rororo* elevates on `12factor <https://12factor.net/config>`_ configuration
principles, which means all values for Settings data structure should come from
environment.

Step 2. Instantiating settings
==============================

After you declare your Settings data structure it is needed to:

1. Instantiate it
2. Assign to the :class:`aiohttp.web.Application` instance

In most cases, it should looks like,

.. code-block:: python

    from aiohttp import web

    from .settings import Settings


    def create_app(
        argv: List[str] = None, *, settings: Settings = None
    ) -> web.Application:
        # Instantiate settings if needed
        if settings is None:
            settings = Settings().from_environ()

        # Instantiate app
        app = web.Application(...)

        # Assign settings to the application for later reusage
        app["settings"] = settings

        # Return app
        return app

You also, might want to "apply" settings by running,

.. code-block:: python

    settings.apply()

right after instantiation. In that case
:func:`rororo.settings.BaseSettings.apply` will call,

- :func:`rororo.settings.setup_locale`
- :func:`rororo.settings.setup_logging`
- :func:`rororo.settings.setup_timezone`

functions with respected settings values.

Configuring Sentry SDK
----------------------

Even :class:`rororo.settings.BaseSettings` contains values to configure
`Sentry <https://sentry.io>`_, it is not designed to call ``sentry_sdk.init``
on :func:`rororo.settings.BaseSettings.apply` run.

You must need to setup `Sentry SDK <https://pypi.org/project/sentry-sdk/>`_ by
yourself like,

.. code-block:: python

    import logging

    import sentry_sdk
    from sentry_sdk.integrations.aiohttp import AioHttpIntegration
    from sentry_sdk.integrations.logging import LoggingIntegartion


    def create_app(argv: List[str] = None) -> web.Application:
        settings = Settings.from_environ()

        if settings.sentry_dsn:
            sentry_sdk.init(
                settings.sentry_dsn,
                environment=settings.level,
                release=settings.sentry_release,
                integrations=(
                    AioHttpIntegration(),
                    LoggingIntegration(event_level=logging.WARNING),
                ),
            )

        ...

Setup shortcut
--------------

There is a :func:`rororo.settings.setup_settings_from_environ` &
:func:`rororo.settings.setup_settings` shortcuts, which apply given Settings
data structure and put given instance into :class:`aiohttp.web.Application`
dict as ``"settings"`` key.

In other words given function is a literally shortcut to,

.. code-block:: python

    settings.apply(...)
    app["settings"] = settings

Step 3. Using settings
======================

In `app.__main__` script
------------------------

If you run your ``app`` not via ``python -m aiohttp.web``, but via application
own ``__main__.py``, it is OK to,

1. Run ``create_app`` factory function
2. Read ``settings`` from resulted app
3. Pass ``host`` / ``port`` and other values to :func:`aiohttp.web.run_app`
   function

In most cases that ``__main__.py`` will look like,

.. code-block:: python

    from aiohttp import web
    from rororo.aio import ACCESS_LOG_FORMAT
    from rororo.settings import APP_SETTINGS_KEY

    from app.app import create_app, logger
    from app.settings import Settings


    if __name__ == "__main__":
        app = create_app()

        settings: Settings = app[APP_SETTINGS_KEY]
        is_dev = settings.is_dev

        if is_dev:
            import aiohttp_autoreload

            aiohttp_autoreload.start()

        web.run_app(
            host=settings.host,
            port=settings.port,
            access_log=logger if is_dev else None,
            access_log_format=ACCESS_LOG_FORMAT,
        )

Within view functions
---------------------

As :class:`aiohttp.web.Request` instance contains link to ``app``, which
requests given view handler, it is straight forward to read the settings within
the view as,

.. code-block:: python

    from aiohttp import web
    from rororo.settings import APP_SETTINGS_KEY


    async def index(request: web.Request) -> web.Response:
        if request.app[APP_SETTINGS_KEY].debug:
            print("Hello, world!")
        return web.json_response(True)

However, as ``aiohttp>=3`` supports sub-apps it is considred to more robust
using :attr:`aiohttp.web.Request.config_dict` for accessing Settings data
structure,

.. code-block:: python

    if request.config_dict[APP_SETTINGS_KEY].debug:
        print("Hello, world!")
