"""
============
rororo.utils
============

Different utility functions, which are common used in web development, like
converting string to int or bool.

"""

from distutils.util import strtobool
from typing import Any, Collection, Optional, Union

from .annotations import T


def ensure_collection(value: Collection[str]) -> Collection[str]:
    """Ensure that given value is a collection, not a single string.

    As passing single string validates ``Collection[str]`` type annotation,
    this function converts given single string to a tuple with one item.

    In all other cases return given value.
    """
    if isinstance(value, str):
        return (value,)
    return value


def to_bool(value: Any) -> bool:
    """Convert string or other Python object to boolean.

    **Rationalle**

    Passing flags is one of the most common cases of using environment vars and
    as values are strings we need to have an easy way to convert them to
    boolean Python value.

    Without this function int or float string values can be converted as false
    positives, e.g. ``bool('0') => True``, but using this function ensure that
    digit flag be properly converted to boolean value.

    :param value: String or other value.
    """
    return bool(strtobool(value) if isinstance(value, str) else value)


def to_int(value: str, default: T = None) -> Union[int, Optional[T]]:
    """Convert given value to int.

    If conversion failed, return default value without raising Exception.

    :param value: Value to convert to int.
    :param default: Default value to use in case of failed conversion.
    """
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
