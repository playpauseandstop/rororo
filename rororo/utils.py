"""
============
rororo.utils
============

Common utilities to use in ``rororo`` and other projects.

"""

import os

import six


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
    if isinstance(value, six.text_type):
        return value
    return value.decode(encoding, errors)
