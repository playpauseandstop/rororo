"""
=============
rororo.schema
=============

Contains all custom and routr's schemas (guards) and validators.

"""

import copy

from routrschema import RequestParams, form, json_body, qs  # noqa
from schemify import anything, opt, validate  # noqa


class defaults(object):
    """
    Simple schema to pass default values to view.
    """
    def __init__(self, **kwargs):
        """
        Initialize object with any keyword arguments.
        """
        self.__dict__.update(kwargs)

    def __call__(self, request, trace):
        """
        Update trace kwargs with defaults values.
        """
        trace.kwargs.update(copy.deepcopy(self.__dict__))
