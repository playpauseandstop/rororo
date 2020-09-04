"""
=============
rororo.logger
=============

Logging utilities to simplify setting up Python logging.

"""

import logging
import sys
from typing import Any, Optional, Union

from .annotations import DictStrAny


class IgnoreErrorsFilter(object):
    """Ignore all warnings and errors from stdout handler."""

    def filter(self, record: logging.LogRecord) -> bool:  # noqa: A003
        """Allow only debug and info log messages to stdout handler."""
        return record.levelname in {"DEBUG", "INFO"}


def default_logging_dict(*loggers: str, **kwargs: Any) -> DictStrAny:
    r"""Prepare logging dict for :func:`logging.config.dictConfig`.

    *rororo* minds to simplify and unify logging configuration for
    ``aiohttp.web`` applications and cause of that the resulted logging config
    will:

    - Only messages from ``loggers`` will be processed
    - Pass all ``DEBUG`` & ``INFO`` logging messages to ``stdout``
    - Pass all other messages to ``stderr``
    - Any logging message will be formatted as:
      ``"%(asctime)s [%(levelname)s:%(name)s] %(message)s"``

    For example, to enable logging for ``aiohttp`` & ``api`` loggers,

    .. code-block:: python

        from logging.config import dictConfig

        dictConfig(default_logging_dict("aiohttp", "api"))

    :param \*loggers: Enable logging for each logger in sequence.
    :param \*\*kwargs: Setup additional logger params via keyword arguments.
    """
    kwargs.setdefault("level", "INFO")
    return {
        "version": 1,
        "disable_existing_loggers": True,
        "filters": {"ignore_errors": {"()": IgnoreErrorsFilter}},
        "formatters": {
            "default": {
                "format": "%(asctime)s [%(levelname)s:%(name)s] %(message)s"
            },
            "naked": {"format": u"%(message)s"},
        },
        "handlers": {
            "stdout": {
                "class": "logging.StreamHandler",
                "filters": ["ignore_errors"],
                "formatter": "default",
                "level": "DEBUG",
                "stream": sys.stdout,
            },
            "stderr": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": "WARNING",
                "stream": sys.stderr,
            },
        },
        "loggers": {
            logger: dict(handlers=["stdout", "stderr"], **kwargs)
            for logger in loggers
        },
    }


def update_sentry_logging(
    logging_dict: DictStrAny,
    sentry_dsn: Optional[str],
    *loggers: str,
    level: Union[str, int] = None,
    **kwargs: Any
) -> None:
    r"""Enable Sentry logging if Sentry DSN passed.

    .. deprecated:: 2.0
        Deprecated in favor of
        `sentry-sdk <https://pypi.org/project/sentry-sdk>`_ and will be removed
        in **3.0**.

    .. note::
        Sentry logging requires `raven <http://pypi.org/project/raven>`_
        library to be installed.

    **Usage**

    .. code-block:: python

        from logging.config import dictConfig

        LOGGING = default_logging_dict()
        SENTRY_DSN = "..."

        update_sentry_logging(LOGGING, SENTRY_DSN)
        dictConfig(LOGGING)

    **Using AioHttpTransport for SentryHandler**

    This will allow to use ``aiohttp.client`` for pushing data to Sentry in
    your ``aiohttp.web`` app, which means elimination of sync calls to Sentry.

    .. code-block:: python

        from raven_aiohttp import AioHttpTransport

        update_sentry_logging(
            LOGGING, SENTRY_DSN, transport=AioHttpTransport
        )

    :param logging_dict: Logging dict.
    :param sentry_dsn:
        Sentry DSN value. If ``None`` do not update logging dict at all.
    :param \*loggers:
        Use Sentry logging for each logger in the sequence. If the sequence is
        empty use Sentry logging to each available logger.
    :param \*\*kwargs: Additional kwargs to be passed to ``SentryHandler``.
    """
    # No Sentry DSN, nothing to do
    if not sentry_dsn:
        return

    # Add Sentry handler
    kwargs["class"] = "raven.handlers.logging.SentryHandler"
    kwargs["dsn"] = sentry_dsn
    logging_dict["handlers"]["sentry"] = dict(
        level=level or "WARNING", **kwargs
    )

    loggers = tuple(logging_dict["loggers"]) if not loggers else loggers
    for logger in loggers:
        # Ignore missing loggers
        logger_dict = logging_dict["loggers"].get(logger)
        if not logger_dict:
            continue

        # Ignore logger from logger config
        if logger_dict.pop("ignore_sentry", False):
            continue

        # Handlers list should exist
        handlers = list(logger_dict.setdefault("handlers", []))
        handlers.append("sentry")
        logger_dict["handlers"] = tuple(handlers)
