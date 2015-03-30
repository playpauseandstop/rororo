"""
=============
rororo.logger
=============

Logging utilities.

"""

import sys

from logging import StreamHandler


class IgnoreErrorsFilter(object):

    """Ignore all warnings and errors from stdout handler."""

    def filter(self, record):
        """Allow only debug and info log messages to stdout handler."""
        return record.levelname in {'DEBUG', 'INFO'}


def default_logging_dict(*loggers, **kwargs):
    r"""Prepare logging dict suitable with ``logging.config.dictConfig``.

    :param \*loggers: Enable logging for given loggers sequence.
    :param \*\*kwargs: Setup additional loggers params via keyword arguments.
    """
    kwargs.setdefault('level', 'INFO')
    return {
        'version': 1,
        'disable_existing_loggers': True,
        'filters': {
            'ignore_errors': {
                '()': IgnoreErrorsFilter,
            },
        },
        'formatters': {
            'default': {
                'format': '%(asctime)s [%(levelname)s:%(name)s] %(message)s',
            },
            'naked': {
                'format': u'%(message)s',
            },
        },
        'handlers': {
            'stdout': {
                'class': StreamHandler,
                'filters': ['ignore_errors'],
                'formatter': 'default',
                'level': 'DEBUG',
                'stream': sys.stdout,
            },
            'stderr': {
                'class': StreamHandler,
                'formatter': 'default',
                'level': 'WARNING',
                'stream': sys.stderr,
            },
        },
        'loggers': {
            logger: dict(handlers=['stdout', 'stderr'], **kwargs)
            for logger in loggers
        },
    }


def update_sentry_logging(logging_dict, sentry_dsn, *loggers):
    r"""Enable Sentry logging if Sentry DSN passed.

    .. note::
        Sentry logging requires `raven <http://pypi.python.org/pypi/raven>`_
        to be installed.

    :param logging_dict: Logging dict.
    :param sentry_dsn:
        Sentry DSN value. If None do not update logging dict at all.
    :param \*loggers: Use Sentry logging for given loggers sequence.
    """
    # No Sentry DSN, nothing to do
    if not sentry_dsn:
        return

    # Add Sentry handler
    logging_dict['handlers']['sentry'] = {
        'level': 'WARNING',
        'class': 'raven.handlers.logging.SentryHandler',
        'dsn': sentry_dsn,
    }

    for logger in loggers:
        # Ignore missing loggers
        logger_dict = logging_dict['loggers'].get(logger)
        if not logger_dict:
            continue

        # Handlers list should exist
        logger_dict.setdefault('handlers', [])
        logger_dict['handlers'].append('sentry')
