import logging
import re
from typing import List, Optional, Union

from jsonschema.exceptions import ValidationError as JsonSchemaValidationError
from openapi_core.schema.exceptions import OpenAPIMappingError
from openapi_core.schema.media_types.exceptions import (
    InvalidContentType,
    InvalidMediaTypeValue,
    OpenAPIMediaTypeError,
)
from openapi_core.schema.parameters.exceptions import (
    EmptyParameterValue,
    InvalidParameterValue,
    MissingParameter,
    MissingRequiredParameter,
    OpenAPIParameterError,
)

from ..annotations import MappingStrStr, TypedDict


ERROR_FIELD_REQUIRED = "Field required"
ERROR_NOT_FOUND_TEMPLATE = "{label} not found"
ERROR_PARAMETER_EMPTY = "Empty parameter value"
ERROR_PARAMETER_INVALID = "Invalid parameter value"
ERROR_PARAMETER_MISSING = "Missing parameter"
ERROR_PARAMETER_REQUIRED = "Parameter required"
OBJECT_LABEL = "Object"

PathItem = Union[int, str]

logger = logging.getLogger(__name__)
required_message_re = re.compile(
    r"^'(?P<field_name>.*)' is a required property$"
)


class OpenAPIError(Exception):
    """Base exception for other OpenAPI exceptions."""

    default_message = "Unhandled OpenAPI error"
    default_headers: MappingStrStr = {}
    status = 500

    def __init__(
        self, message: str = None, *, headers: MappingStrStr = None
    ) -> None:
        super().__init__(message or self.default_message)
        self.headers = headers or self.default_headers


class ConfigurationError(OpenAPIError):
    """Wrong OpenAPI configuration."""

    default_message = "OpenAPI schema configuration error"


class ContextError(OpenAPIError):
    """Attempt to use context when it is not available."""

    default_message = "OpenAPI context missed in request"


class OperationError(OpenAPIError):
    """Invalid OpenAPI operation."""

    default_message = "OpenAPI operation not found"


class SecurityError(OpenAPIError):
    """Request is not secured, but should."""

    default_message = "Not authenticated"
    status = 403


class BasicSecurityError(SecurityError):
    """Basic authentication is not provided."""

    default_headers = {"www-authenticate": "basic"}
    status = 401


class InvalidCredentials(SecurityError):
    """Invalid credentials provided for authentication."""

    default_message = "Invalid credentials"
    status = 403


class BasicInvalidCredentials(InvalidCredentials):
    """Invalid credentials provided for basic authentication."""

    default_headers = {"www-authenticate": "basic"}
    status = 401


class ObjectDoesNotExist(OpenAPIError):
    """Object does not exist basic error."""

    default_message = ERROR_NOT_FOUND_TEMPLATE.format(label=OBJECT_LABEL)
    status = 404

    def __init__(
        self,
        label: str = OBJECT_LABEL,
        *,
        message: str = None,
        headers: MappingStrStr = None,
    ) -> None:
        super().__init__(
            message or ERROR_NOT_FOUND_TEMPLATE.format(label=label),
            headers=headers,
        )
        self.label = label


class ValidationErrorItem(TypedDict):
    loc: List[PathItem]
    message: str


class ValidationError(OpenAPIError):
    """Request / response validation error."""

    default_message = "Validation error"
    status = 422

    def __init__(
        self, *, message: str = None, errors: List[ValidationErrorItem] = None,
    ) -> None:
        super().__init__(message or self.default_message)

        self.errors = errors
        self.data = {"detail": errors} if errors else None

    @classmethod
    def from_request_errors(  # type: ignore
        cls, errors: List[OpenAPIMappingError]
    ) -> "ValidationError":
        parameters = []
        body = []

        for err in errors:
            if isinstance(err, OpenAPIParameterError):
                details = get_parameter_error_details(err)
                if details:
                    parameters.append(details)
            elif isinstance(err, OpenAPIMediaTypeError):
                details = get_media_type_error_details(["body"], err)
                if details:
                    body.append(details)
            else:
                logger.debug(
                    "Unhandled request validation error",
                    extra={"err": err, "err_type": str(type(err))},
                )

        return cls(
            message="Request parameters or body validatione error",
            errors=parameters + body,
        )


def ensure_loc(loc: List[PathItem]) -> List[PathItem]:
    return [item for item in loc if item != ""]


def get_media_type_error_details(
    loc: List[PathItem], err: OpenAPIMediaTypeError
) -> Optional[ValidationErrorItem]:
    if isinstance(err, InvalidContentType):
        return {
            "loc": loc,
            "message": (
                f"Schema missing for following mimetype: {err.mimetype}"
            ),
        }

    if isinstance(err, InvalidMediaTypeValue):
        maybe_json_schema_err = getattr(
            err.original_exception, "__context__", None
        )
        if maybe_json_schema_err and isinstance(
            maybe_json_schema_err, JsonSchemaValidationError
        ):
            message = maybe_json_schema_err.message
            path = list(maybe_json_schema_err.absolute_path)
            matched = required_message_re.match(message)

            if matched:
                return {
                    "loc": ensure_loc(
                        loc + path + [matched.groupdict()["field_name"]]
                    ),
                    "message": ERROR_FIELD_REQUIRED,
                }

            return {
                "loc": ensure_loc(loc + path),
                "message": maybe_json_schema_err.message,
            }

    return None


def get_parameter_error_details(
    err: OpenAPIParameterError,
) -> Optional[ValidationErrorItem]:
    parameter_name: str = getattr(err, "name", None)
    if parameter_name is None:
        return None

    message = {
        EmptyParameterValue: ERROR_PARAMETER_EMPTY,
        InvalidParameterValue: ERROR_PARAMETER_INVALID,
        MissingParameter: ERROR_PARAMETER_MISSING,
        MissingRequiredParameter: ERROR_PARAMETER_REQUIRED,
    }[type(err)]

    return {"loc": ["parameters", parameter_name], "message": message}
