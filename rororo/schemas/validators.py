"""
=========================
rororo.schemas.validators
=========================

Customize default JSON Schema Draft 4 validator.

"""

from jsonschema.validators import Draft4Validator

from .utils import defaults


class Validator(Draft4Validator):

    """Customize default JSON Schema validator.

    This customization allows:

    * Use tuples for "array" data type

    """

    DEFAULT_TYPES = defaults({
        'array': (list, tuple),
    }, Draft4Validator.DEFAULT_TYPES)
