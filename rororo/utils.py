"""
============
rororo.utils
============

Common utilities to use in ``rororo`` and other projects.

"""

import os
import types

from . import compat


def absdir(dirname, base):
    """
    Prepend ``base`` path to ``dirname`` path if it relative.
    """
    if os.path.isabs(dirname):
        return dirname
    return os.path.abspath(os.path.join(base, dirname))


def force_unicode(value, encoding='utf-8', errors='ignore'):
    """
    Cast value to unicode representation.
    """
    if isinstance(value, compat.text_type):
        return value
    return value.decode(encoding, errors)


def get_commands(module):
    """
    Get commands from given Python module.
    """
    # First of all read all public module members, prefer getting they from
    # __all__
    if hasattr(module, '__all__'):
        names = module.__all__
    else:
        names = [name for name in dir(module) if not name.startswith('_')]

    items = [getattr(module, name) for name in names]
    return filter(
        lambda item: callable(item) and isinstance(item, types.FunctionType),
        items
    )
