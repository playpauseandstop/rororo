from collections import deque
from typing import Any, Dict, List, Tuple

import pyrsistent
from email_validator import EmailNotValidError, validate_email
from jsonschema.exceptions import FormatError
from openapi_core.casting.schemas.exceptions import CastError as CoreCastError
from openapi_core.exceptions import OpenAPIError as CoreOpenAPIError
from openapi_core.spec.paths import SpecPath
from openapi_core.unmarshalling.schemas.exceptions import InvalidSchemaValue
from openapi_core.unmarshalling.schemas.formatters import Formatter
from openapi_core.validation.request.datatypes import (
    OpenAPIRequest,
    RequestParameters,
)
from openapi_core.validation.request.validators import (
    RequestValidator as CoreRequestValidator,
)
from openapi_core.validation.response.datatypes import OpenAPIResponse
from openapi_core.validation.response.validators import (
    ResponseValidator as CoreResponseValidator,
)
from openapi_core.validation.validators import (
    BaseValidator as CoreBaseValidator,
)

from ..annotations import MappingStrAny
from .annotations import ValidateEmailKwargsDict
from .data import OpenAPIParameters, to_openapi_parameters
from .exceptions import CastError, ValidationError
from .security import SecurityProviderFactory
from .utils import get_base_url


class EmailFormatter(Formatter):
    """Formatter to support email strings.

    Use `email-validator <https://pypi.org/project/email-validator>`_ library
    to ensure that given string is a valid email.
    """

    kwargs: ValidateEmailKwargsDict

    def __init__(self, kwargs: ValidateEmailKwargsDict = None) -> None:
        self.kwargs: ValidateEmailKwargsDict = kwargs or {}

    def validate(self, value: str) -> bool:
        try:
            validate_email(value, **self.kwargs)
        except EmailNotValidError as err:
            raise FormatError(f"{value!r} is not an 'email'", cause=err)
        return True


class BaseValidator(CoreBaseValidator):
    def _get_param_or_header_value(
        self, param_or_header: Any, location, name=None
    ):
        try:
            return super()._get_param_or_header_value(
                param_or_header, location, name
            )
        except CoreCastError as err:
            raise CastError(
                name=param_or_header["name"],
                value=err.value,
                type=err.type,
            )
        except InvalidSchemaValue as err:
            if isinstance(param_or_header, SpecPath):
                for schema_error in err.schema_errors:
                    schema_error.path = schema_error.relative_path = deque(
                        [param_or_header["name"]]
                    )
            raise err


class RequestValidator(BaseValidator, CoreRequestValidator):
    @property
    def security_provider_factory(self):
        return SecurityProviderFactory()

    def _get_parameters(
        self, request: OpenAPIRequest, path, operation
    ) -> Tuple[RequestParameters, List[CoreOpenAPIError]]:
        """
        Distinct parameters errors from body errors to supply proper validation
        error response.
        """
        parameters, errors = super()._get_parameters(request, path, operation)
        if errors:
            raise ValidationError.from_request_errors(
                errors, base_loc=["parameters"]
            )
        return parameters, errors


class ResponseValidator(BaseValidator, CoreResponseValidator):
    ...


def get_custom_formatters(
    *, validate_email_kwargs: ValidateEmailKwargsDict = None
) -> Dict[str, Formatter]:
    return {"email": EmailFormatter(validate_email_kwargs)}


def validate_core_request(
    spec: SpecPath,
    core_request: OpenAPIRequest,
    *,
    validate_email_kwargs: ValidateEmailKwargsDict = None,
) -> Tuple[MappingStrAny, OpenAPIParameters, Any]:
    """
    Instead of validating request parameters & body in two calls, validate them
    at once with passing custom formatters.
    """
    custom_formatters = get_custom_formatters(
        validate_email_kwargs=validate_email_kwargs
    )

    validator = RequestValidator(
        spec,
        custom_formatters=custom_formatters,
        base_url=get_base_url(core_request),
    )
    result = validator.validate(core_request)

    if result.errors:
        raise ValidationError.from_request_errors(result.errors)

    return (
        result.security,
        to_openapi_parameters(result.parameters),
        pyrsistent.freeze(result.body),
    )


def validate_core_response(
    spec: SpecPath,
    core_request: OpenAPIRequest,
    core_response: OpenAPIResponse,
    *,
    validate_email_kwargs: ValidateEmailKwargsDict = None,
) -> Any:
    """Pass custom formatters for validating response data."""
    custom_formatters = get_custom_formatters(
        validate_email_kwargs=validate_email_kwargs
    )

    validator = ResponseValidator(
        spec,
        custom_formatters=custom_formatters,
        base_url=get_base_url(core_request),
    )
    result = validator.validate(core_request, core_response)

    if result.errors:
        raise ValidationError.from_response_errors(result.errors)

    return result.data
