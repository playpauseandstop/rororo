from typing import Any, List, Tuple

import pyrsistent
from email_validator import EmailNotValidError, validate_email
from jsonschema.exceptions import FormatError
from openapi_core.exceptions import OpenAPIError
from openapi_core.schema.operations.models import Operation
from openapi_core.schema.specs.models import Spec
from openapi_core.unmarshalling.schemas.formatters import Formatter
from openapi_core.validation.request.datatypes import (
    OpenAPIRequest,
    RequestParameters,
)
from openapi_core.validation.request.validators import (
    RequestValidator as BaseRequestValidator,
)
from openapi_core.validation.response.datatypes import OpenAPIResponse
from openapi_core.validation.response.validators import ResponseValidator

from .data import OpenAPIParameters, to_openapi_parameters
from .exceptions import ValidationError
from .security import validate_security
from .utils import get_base_url
from ..annotations import MappingStrAny


class EmailFormatter(Formatter):
    def validate(self, value: str) -> bool:
        try:
            validate_email(value)
        except EmailNotValidError as err:
            raise FormatError(f"{value!r} is not an 'email'", cause=err)
        return True


CUSTOM_FORMATTERS = {"email": EmailFormatter()}


class RequestValidator(BaseRequestValidator):
    def _get_parameters(
        self, request: OpenAPIRequest, params: MappingStrAny
    ) -> Tuple[RequestParameters, List[OpenAPIError]]:
        parameters, errors = super()._get_parameters(request, params)
        if errors:
            raise ValidationError.from_request_errors(
                errors, unmarshal_loc=["parameters"]
            )
        return parameters, errors

    def _get_security(
        self, request: OpenAPIRequest, operation: Operation
    ) -> MappingStrAny:
        return validate_security(self, request, operation)


def validate_request(
    spec: Spec, core_request: OpenAPIRequest
) -> Tuple[Any, OpenAPIParameters, Any]:
    """
    Instead of validating request parameters & body in two calls, validate them
    at once with passing custom formatters.
    """
    validator = RequestValidator(
        spec,
        custom_formatters=CUSTOM_FORMATTERS,
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


def validate_response(
    spec: Spec, core_request: OpenAPIRequest, core_response: OpenAPIResponse,
) -> Any:
    """Pass custom formatters on validating response data."""
    validator = ResponseValidator(
        spec,
        custom_formatters=CUSTOM_FORMATTERS,
        base_url=get_base_url(core_request),
    )
    result = validator.validate(core_request, core_response)

    if result.errors:
        raise ValidationError.from_response_errors(result.errors)

    return result.data
