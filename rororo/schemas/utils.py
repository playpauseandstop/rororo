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


def validate_func_factory(validator_class):
    """Factory to return default validate function for Schema.

    :param validator_class: JSONSchema suitable validator class.
    """
    def validate_func(schema, pure_data):
        """Validate schema with given data.

        :param schema: Schema representation to use.
        :param pure_data: Pure data to validate.
        """
        return validator_class(schema).validate(pure_data)
    return validate_func
