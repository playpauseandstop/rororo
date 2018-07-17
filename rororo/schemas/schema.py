"""
=====================
rororo.schemas.schema
=====================

Implement class for validating request and response data against JSON Schema.

"""

import logging
import types
from typing import Any, Callable, Optional, Type  # noqa: F401

from jsonschema.exceptions import ValidationError

from .exceptions import Error
from .utils import AnyMapping, defaults, validate_func_factory, ValidateFunc
from .validators import DefaultValidator


__all__ = ('Schema', )


logger = logging.getLogger(__name__)


class Schema(object):

    """Validate request and response data against JSON Schema."""

    __slots__ = (
        'error_class', 'module', 'response_factory', 'validate_func',
        'validation_error_class', 'validator_class', '_valid_request',
    )

    def __init__(self,
                 module: types.ModuleType,
                 *,
                 response_factory: Callable[..., Any]=None,
                 error_class: Any=None,
                 validator_class: Any=DefaultValidator,
                 validation_error_class: Type[Exception]=ValidationError,
                 validate_func: ValidateFunc=None) -> None:
        """Initialize Schema object.

        :param module: Module contains at least request and response schemas.
        :param response_factory: Put valid response data to this factory func.
        :param error_class:
            Wrap all errors in given class. If empty real errors would be
            reraised.
        :param validator_class:
            Validator class to use for validating request and response data.
            By default: ``rororo.schemas.validators.DefaultValidator``
        :param validation_error_class:
            Error class to be expected in case of validation error. By default:
            ``jsonschema.exceptions.ValidationError``
        :param validate_func:
            Validate function to be called for validating request and response
            data. Function will receive 2 args: ``schema`` and ``pure_data``.
            By default: ``None``
        """
        self._valid_request = None  # type: Optional[bool]

        self.module = module
        self.response_factory = response_factory
        self.error_class = error_class

        self.validator_class = validator_class
        self.validate_func = (
            validate_func or
            validate_func_factory(validator_class))
        self.validation_error_class = validation_error_class

    def make_error(self,
                   message: str,
                   *,
                   error: Exception=None,
                   # ``error_class: Type[Exception]=None`` doesn't work on
                   # Python 3.5.2, but that is exact version ran by Read the
                   # Docs :( More info: http://stackoverflow.com/q/42942867
                   error_class: Any=None) -> Exception:
        """Return error instantiated from given message.

        :param message: Message to wrap.
        :param error: Validation error.
        :param error_class:
            Special class to wrap error message into. When omitted
            ``self.error_class`` will be used.
        """
        if error_class is None:
            error_class = self.error_class if self.error_class else Error
        return error_class(message)

    def make_response(self,
                      data: Any=None,
                      **kwargs: Any) -> Any:
        r"""Validate response data and wrap it inside response factory.

        :param data: Response data. Could be ommited.
        :param \*\*kwargs: Keyword arguments to be passed to response factory.
        """
        if not self._valid_request:
            logger.error('Request not validated, cannot make response')
            raise self.make_error('Request not validated before, cannot make '
                                  'response')

        if data is None and self.response_factory is None:
            logger.error('Response data omit, but no response factory is used')
            raise self.make_error('Response data could be omitted only when '
                                  'response factory is used')

        response_schema = getattr(self.module, 'response', None)
        if response_schema is not None:
            self._validate(data, response_schema)

        if self.response_factory is not None:
            return self.response_factory(
                *([data] if data is not None else []),
                **kwargs)
        return data

    def validate_request(self,
                         data: Any,
                         *additional: AnyMapping,
                         merged_class: Type[dict]=dict) -> Any:
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
            logger.error(
                'Request schema should be defined',
                extra={'schema_module': self.module,
                       'schema_module_attrs': dir(self.module)})
            raise self.make_error('Request schema should be defined')

        # Merge base and additional data dicts, but only if additional data
        # dicts have been supplied
        if isinstance(data, dict) and additional:
            data = merged_class(self._merge_data(data, *additional))

        try:
            self._validate(data, request_schema)
        finally:
            self._valid_request = False

        self._valid_request = True

        processor = getattr(self.module, 'request_processor', None)
        return processor(data) if processor else data

    def _merge_data(self, data: AnyMapping, *additional: AnyMapping) -> dict:
        r"""Merge base data and additional dicts.

        :param data: Base data.
        :param \*additional: Additional data dicts to be merged into base dict.
        """
        return defaults(
            dict(data) if not isinstance(data, dict) else data,
            *(dict(item) for item in additional))

    def _pure_data(self, data: Any) -> Any:
        """
        If data is dict-like object, convert it to pure dict instance, so it
        will be possible to pass to default ``jsonschema.validate`` func.

        :param data: Request or response data.
        """
        if not isinstance(data, dict) and not isinstance(data, list):
            try:
                return dict(data)
            except TypeError:
                ...
        return data

    def _validate(self, data: Any, schema: AnyMapping) -> Any:
        """Validate data against given schema.

        :param data: Data to validate.
        :param schema: Schema to use for validation.
        """
        try:
            return self.validate_func(schema, self._pure_data(data))
        except self.validation_error_class as err:
            logger.error(
                'Schema validation error',
                exc_info=True,
                extra={'schema': schema, 'schema_module': self.module})
            if self.error_class is None:
                raise
            raise self.make_error('Validation Error', error=err) from err
