"""
====================
rororo.schemas.utils
====================

Utilities for Schema package.

"""


def defaults(current, *args):
    r"""Override current dict with defaults values.

    :param current: Current dict.
    :param \*args: Sequence with default data dicts.
    """
    for data in args:
        for key, value in data.items():
            current.setdefault(key, value)
    return current
