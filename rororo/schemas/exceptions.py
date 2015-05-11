"""
=========================
rororo.schemas.exceptions
=========================

Exceptions for Schemas.

.. note:: If data cannot be validate against given schema ValidationError from
   ``jsonschema`` library would be raised, not ``rororo.schemas.Error``.

"""


class Error(Exception):

    """Base Schema exception."""
