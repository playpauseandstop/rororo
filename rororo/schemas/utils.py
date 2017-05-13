"""
====================
rororo.schemas.utils
====================

Utilities for Schema package.

"""

from typing import Any, Callable, Mapping


AnyMapping = Mapping[Any, Any]
ValidateFunc = Callable[[AnyMapping, AnyMapping], AnyMapping]


def defaults(current: dict, *args: AnyMapping) -> dict:
    r"""Override current dict with defaults values.

    :param current: Current dict.
    :param \*args: Sequence with default data dicts.
    """
    for data in args:
        for key, value in data.items():
            current.setdefault(key, value)
    return current


def validate_func_factory(validator_class: Any) -> ValidateFunc:
    """Provide default function for Schema validation.

    :param validator_class: JSONSchema suitable validator class.
    """
    def validate_func(schema: AnyMapping, pure_data: AnyMapping) -> AnyMapping:
        """Validate schema with given data.

        :param schema: Schema representation to use.
        :param pure_data: Pure data to validate.
        """
        return validator_class(schema).validate(pure_data)
    return validate_func
