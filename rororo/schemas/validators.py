"""
=========================
rororo.schemas.validators
=========================

Customize default JSON Schema Draft 4 validator.

"""

from typing import Any, Iterator

from jsonschema.exceptions import ValidationError
from jsonschema.validators import Draft4Validator, extend

from .utils import defaults


class Validator(Draft4Validator):

    """Customize default JSON Schema validator.

    This customization allows:

    * Use tuples for "array" data type

    """

    DEFAULT_TYPES = defaults({
        'array': (list, tuple),
    }, Draft4Validator.DEFAULT_TYPES)  # type: dict


def extend_with_default(validator_class: Any) -> Any:
    """Append defaults from schema to instance need to be validated.

    :param validator_class: Apply the change for given validator class.
    """
    validate_properties = validator_class.VALIDATORS['properties']

    def set_defaults(validator: Any,
                     properties: dict,
                     instance: dict,
                     schema: dict) -> Iterator[ValidationError]:
        for prop, subschema in properties.items():
            if 'default' in subschema:
                instance.setdefault(prop, subschema['default'])

        for error in validate_properties(
            validator, properties, instance, schema,
        ):
            yield error  # pragma: no cover

    return extend(validator_class, {'properties': set_defaults})


DefaultValidator = extend_with_default(Validator)
