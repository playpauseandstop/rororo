"""
=========================
rororo.schemas.validators
=========================

Customize default JSON Schema Draft 4 validator.

"""

from jsonschema.validators import Draft4Validator, extend

from .utils import defaults


class Validator(Draft4Validator):

    """Customize default JSON Schema validator.

    This customization allows:

    * Use tuples for "array" data type

    """

    DEFAULT_TYPES = defaults({
        'array': (list, tuple),
    }, Draft4Validator.DEFAULT_TYPES)


def extend_with_default(validator_class):
    """Append defaults from schema to instance need to be validated.

    :param validator_class: Apply the change for given validator class.
    """
    validate_properties = validator_class.VALIDATORS['properties']

    def set_defaults(validator, properties, instance, schema):
        for prop, subschema in properties.items():
            if 'default' in subschema:
                instance.setdefault(prop, subschema['default'])

        for error in validate_properties(
            validator, properties, instance, schema,
        ):
            yield error  # pragma: no cover

    return extend(validator_class, {'properties': set_defaults})


DefaultValidator = extend_with_default(Validator)
