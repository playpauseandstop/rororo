"""
=====================
rororo.schemas.schema
=====================

Implement class for validating request and response data against JSON Schema.

"""

from jsonschema.exceptions import ValidationError
from jsonschema.validators import validate

from .exceptions import Error
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

    def validate_request(self, data):
        """Validate request data against request schema from module.

        :param data: Request data.
        """
        request_schema = getattr(self.module, 'request', None)
        if request_schema is None:
            raise self.make_error('Request schema should be defined')

        try:
            self._validate(data, request_schema)
        finally:
            self._valid_request = False

        self._valid_request = True

        processor = getattr(self.module, 'request_processor', None)
        return processor(data) if processor else data

    def _validate(self, data, schema):
        """Validate data against given schema.

        :param data: Data to validate.
        :param schema: Schema to use for validation.
        """
        try:
            return validate(data, schema, self.validator)
        except ValidationError as err:
            if self.error_class is None:
                raise
            raise self.make_error('Validation Error', error=err) from err
