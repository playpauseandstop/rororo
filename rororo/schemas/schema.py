"""
=====================
rororo.schemas.schema
=====================

Implement class for validating request and response data against JSON Schema.

"""

import types

try:
    from aiohttp.multidict import MultiDict, MultiDictProxy
except ImportError:  # pragma: no cover
    MultiDict, MultiDictProxy = None, None

from jsonschema.exceptions import ValidationError
from jsonschema.validators import validate

from .exceptions import Error
from .utils import defaults
from .validators import Validator


class Schema(object):

    """Validate request and response data against JSON Schema."""

    __slots__ = ('error_class', 'module', 'response_factory', 'validator',
                 '_valid_request')

    def __init__(self, module, *, response_factory=None, error_class=None,
                 validator=None):
        """Initialize Schema object.

        :param module: Module contains at least request and response schemas.
        :param response_factory: Put valid response data to this factory func.
        :param error_class:
            Wrap all errors in given class. If empty real errors would be
            reraised.
        :param validator: Use given validator instead of standart one.
        """
        self._valid_request = None
        self.error_class = error_class
        self.module = module
        self.response_factory = response_factory
        self.validator = validator or Validator

    def make_error(self, message, *, error=None):
        """Return error instantiated from given message.

        :param message: Message to wrap.
        :param error: Validation error.
        """
        return (Error(message)
                if self.error_class is None
                else self.error_class(message))

    def make_response(self, data, **kwargs):
        r"""Validate response data and wrap it inside response factory.

        :param data: Response data.
        :param \*\*kwargs: Keyword arguments to be passed to response factory.
        """
        if not self._valid_request:
            raise self.make_error('Request not validated before, cannot make '
                                  'response')

        response_schema = getattr(self.module, 'response', None)
        if response_schema is not None:
            self._validate(data, response_schema)

        if self.response_factory is not None:
            return self.response_factory(data, **kwargs)
        return data

    def validate_request(self, data, *additional, merged_class=dict):
        r"""Validate request data against request schema from module.

        :param data: Request data.
        :param \*additional:
            Additional data dicts to be merged with base request data.
        :param merged_class:
            When additional data dicts supplied method by default will return
            merged **dict** with all data, but you can customize things to
            use read-only dict or any other additional class or callable.
        """
        request_schema = getattr(self.module, 'request', None)
        if request_schema is None:
            raise self.make_error('Request schema should be defined')

        # Merge base and additional data dicts, but only if additional data
        # dicts have been supplied
        if additional:
            data = merged_class(self._merge_data(data, *additional))

        try:
            self._validate(data, request_schema)
        finally:
            self._valid_request = False

        self._valid_request = True

        processor = getattr(self.module, 'request_processor', None)
        return processor(data) if processor else data

    def _merge_data(self, data, *additional):
        r"""Merge base data and additional dicts.

        :param data: Base data.
        :param \*additional: Additional data dicts to be merged into base dict.
        """
        data = self._pure_data(data)
        for item in additional:
            data = defaults(data, self._pure_data(item))
        return data

    def _pure_data(self, data):
        """
        Convert multi-dicts or any other custom dicts to normal dicts to be
        compatible with ``jsonschema.validate`` function.

        :param data: Python dict or other object.
        """
        dict_types = [types.MappingProxyType]
        if MultiDict is not None:  # pragma: no branch
            dict_types.extend((MultiDict, MultiDictProxy))

        if isinstance(data, tuple(dict_types)):
            return dict(data)

        return data

    def _validate(self, data, schema):
        """Validate data against given schema.

        :param data: Data to validate.
        :param schema: Schema to use for validation.
        """
        try:
            return validate(self._pure_data(data), schema, self.validator)
        except ValidationError as err:
            if self.error_class is None:
                raise
            raise self.make_error('Validation Error', error=err) from err
