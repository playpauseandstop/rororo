"""
=============
rororo.schema
=============

Contains all custom and routr's schemas (guards) and validators.

"""

import copy

from .utils import inject_module


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


# Include schemas from routrschema module
inject_module('routrschema',
              locals(),
              include_attr=('RequestParams', 'form', 'json_body', 'qs'))

# Include validators from schemify module
inject_module('schemify',
              locals(),
              include_attr=('anything', 'opt', 'validate'))
