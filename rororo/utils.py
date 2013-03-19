"""
============
rororo.utils
============

Common utilities to use in ``rororo`` and other projects.

"""

import os


def absdir(dirname, base):
    """
    Prepend ``base`` path to ``dirname`` path if it relative.
    """
    if os.path.isabs(dirname):
        return dirname
    return os.path.abspath(os.path.join(base, dirname))
