from functools import partial
from typing import Any, Dict, List, Tuple

import pyrsistent
from email_validator import EmailNotValidError, validate_email
from isodate import parse_datetime
from jsonschema.exceptions import FormatError
from openapi_core.exceptions import OpenAPIError
from openapi_core.schema.operations.models import Operation
from openapi_core.schema.schemas.enums import SchemaFormat
from openapi_core.schema.specs.models import Spec
from openapi_core.unmarshalling.schemas.enums import UnmarshalContext
from openapi_core.unmarshalling.schemas.factories import (
    SchemaUnmarshallersFactory as BaseSchemaUnmarshallersFactory,
)
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
from openapi_schema_validator._format import oas30_format_checker

from .data import OpenAPIParameters, to_openapi_parameters
from .exceptions import ValidationError
from .security import validate_security
from .utils import get_base_url
from ..annotations import MappingStrAny


DATE_TIME_FORMATTER = Formatter.from_callables(
    partial(oas30_format_checker.check, format="date-time"), parse_datetime,
)


class EmailFormatter(Formatter):
    def validate(self, value: str) -> bool:
        try:
            validate_email(value)
        except EmailNotValidError as err:
            raise FormatError(f"{value!r} is not an 'email'", cause=err)
        return True


class SchemaUnmarshallersFactory(BaseSchemaUnmarshallersFactory):
    def get_formatter(
        self,
        default_formatters: Dict[str, Formatter],
        type_format: str = None,
    ) -> Formatter:
        if type_format == SchemaFormat.DATETIME.value:
            return DATE_TIME_FORMATTER
        return super().get_formatter(default_formatters, type_format)


CUSTOM_FORMATTERS = {"email": EmailFormatter()}


class BaseValidator(CoreBaseValidator):
    def _unmarshal(
        self, param_or_media_type: Any, value: Any, context: UnmarshalContext
    ) -> Any:
        if not param_or_media_type.schema:
            return value

        unmarshallers_factory = SchemaUnmarshallersFactory(
            self.spec._resolver, self.custom_formatters, context=context,
        )
        unmarshaller = unmarshallers_factory.create(param_or_media_type.schema)
        return unmarshaller(value)


class RequestValidator(BaseValidator, CoreRequestValidator):
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

    def _unmarshal(  # type: ignore
        self, param_or_media_type: Any, value: Any
    ) -> Any:
        return super()._unmarshal(
            param_or_media_type, value, UnmarshalContext.REQUEST
        )


class ResponseValidator(BaseValidator, CoreResponseValidator):
    def _unmarshal(  # type: ignore
        self, param_or_media_type: Any, value: Any
    ) -> Any:
        return super()._unmarshal(
            param_or_media_type, value, UnmarshalContext.RESPONSE
        )


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
