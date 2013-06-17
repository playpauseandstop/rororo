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
