"""
============
rororo.utils
============

Common utilities to use in ``rororo`` and other projects.

"""

import copy
import logging
import os
import time
import types

from collections import Container

from routr.utils import import_string

from . import compat


def absdir(dirname, base):
    """
    Prepend ``base`` path to ``dirname`` path if it relative.
    """
    if os.path.isabs(dirname):
        return dirname
    return os.path.abspath(os.path.join(base, dirname))


def dict_combine(first, second, do_copy=True):
    """
    Combine two dicts, but without affects to original dicts.
    """
    copied = copy.deepcopy(first) if do_copy else first

    for key, value in compat.iteritems(second):
        exists = key in copied

        if exists and isinstance(copied[key], dict):
            assert isinstance(value, dict)
            copied[key] = dict_combine(copied[key], value)
        elif exists and isinstance(copied[key], list):
            assert isinstance(value, list)
            copied[key] = copied[key] + value
        elif exists and isinstance(copied[key], set):
            assert isinstance(value, set)
            copied[key] = copied[key] ^ value
        elif exists and isinstance(copied[key], tuple):
            assert isinstance(value, tuple)
            copied[key] = copied[key] + value
        else:
            copied[key] = value

    return copied


def force_unicode(value, encoding='utf-8', errors='ignore'):
    """
    Cast value to unicode representation.
    """
    if isinstance(value, compat.text_type):
        return value
    return value.decode(encoding, errors)


def get_commands(commands):
    """
    Safe processing list of commands. Understands raw functions and Python
    modules to search commands there.
    """
    def get_commands_from_module(module):
        """
        Get commands from Python module.
        """
        if hasattr(module, '__all__'):
            names = module.__all__
        else:
            names = [name for name in dir(module) if not name.startswith('_')]

        items = [getattr(module, name) for name in names]
        return [item
                for item in items
                if callable(item) and isinstance(item, types.FunctionType)]

    safe = lambda item: (get_commands_from_module(item)
                         if not callable(item)
                         else [item])
    return [cmd for command in commands for cmd in safe(command)]


def inject_exceptions(module, namespace, overwrite=True, fail_silently=False):
    """
    Inject all exceptions from ``module`` to ``namespace`` dict-like instance.

    See also: ``inject_module`` and ``inject_settings``.
    """
    include_func = lambda value: (isinstance(value, type) and
                                  issubclass(value, Exception))
    return inject_module(module,
                         namespace,
                         include_value=include_func,
                         overwrite=overwrite,
                         fail_silently=fail_silently)


def inject_module(module, namespace, include_attr=None, ignore_attr=None,
                  include_value=None, ignore_value=None, overwrite=True,
                  fail_silently=False):
    """
    Inject all attributes with their values from ``module`` to ``namespace``
    dict-like instance.

    Module should be a path or already imported Python module.

    If you need to include only specified attributes or values you should pass
    string, container or callable to ``include_attr`` and ``include_value``
    args. Same to ignorance and ``ignore_attr``, ``ignore_value`` args.

    By default, attributes would be overwritten in namespace if they already
    setup, to disable use ``overwrite=False``.

    Pass ``fail_silently=True`` to supress raising ``ImportError`` if settings
    module was a path and unable to import.
    """
    def checker(mixed, value):
        """
        Check that mixed is not null and value is in mixed or returns positive
        after call.
        """
        if mixed is not None:
            if callable(mixed):
                return mixed(value)
            elif (
                isinstance(mixed, Container) and
                not isinstance(mixed, compat.string_types)
            ):
                return value in mixed
            return value == mixed
        return False

    if isinstance(module, compat.string_types):
        try:
            imported = import_string(module)
        except ImportError:
            if fail_silently:
                return False
            raise
    else:
        imported = module

    for attr in dir(imported):
        value = getattr(imported, attr)

        if (
            checker(ignore_attr, attr) or
            checker(ignore_value, value) or
            (not overwrite and attr in namespace)
        ):
            continue

        if (
            checker(include_attr, attr) or
            checker(include_value, value) or
            (not include_attr and not include_value)
        ):
            namespace[attr] = value

    return True


def inject_settings(settings, namespace, overwrite=True, fail_silently=False):
    """
    Import all possible settings from ``settings`` module and place them to
    ``namespace`` dict-like instance.

    Settings module should be a path or already imported Python module.

    If settings module doesn't exist, ``ImportError`` would be raised, but you
    should supress this approach by passing ``fail_silently=True``.
    """
    ignore_func = lambda attr: not attr.isupper() or attr.startswith('_')
    return inject_module(settings,
                         namespace,
                         ignore_attr=ignore_func,
                         overwrite=overwrite,
                         fail_silently=fail_silently)


def make_debug(enabled=False, extra=None, level=None, instance=None):
    """
    Factory to make function to provide extended logs when application works
    in debug mode.
    """
    def debug(message, debug_message, **kwargs):
        """
        Concat and log normal log message with debug message when application
        works in debug mode.
        """
        if enabled:
            message = u''.join((message, debug_message))

        local_extra = extra or kwargs.pop('extra', {})
        local_level = level or kwargs.pop('level', 'debug')
        local_instance = instance or kwargs.pop('instance', None)
        local_instance = local_instance or logging.getLogger(__name__)

        start_time = kwargs.pop('start_time', None)

        if start_time:
            local_extra['time'] = time.time() - start_time

        message = message.format(**local_extra)
        kwargs['extra'] = local_extra

        getattr(local_instance, local_level)(message, **kwargs)

    return debug


def setup_logging(base, local=None):
    """
    Combine base and local logging dicts if possible and setup logging using
    ``dictConfig`` method.
    """
    config = dict_combine(base, local) if local else base

    if config:
        compat.logging_config(config)


def setup_timezone(timezone):
    """
    Setup timezone if possible.
    """
    if timezone and hasattr(time, 'tzset'):
        tz_root = '/usr/share/zoneinfo'
        tz_filename = os.path.join(tz_root, *(timezone.split('/')))

        if os.path.exists(tz_root) and not os.path.exists(tz_filename):
            raise ValueError('Incorrect timezone value: {0}'.format(timezone))

        os.environ['TZ'] = timezone
        time.tzset()
