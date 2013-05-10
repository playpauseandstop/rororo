"""
=============
rororo.schema
=============

Additional schemas (guards) to routr's: form, qs and json_body.

"""

import copy


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
