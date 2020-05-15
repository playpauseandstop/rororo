import logging
import re
from typing import Any, Dict, List, Union

import attr
from jsonschema.exceptions import ValidationError as JsonSchemaValidationError
from openapi_core.casting.schemas.exceptions import CastError as CoreCastError
from openapi_core.deserializing.exceptions import DeserializeError
from openapi_core.deserializing.parameters.exceptions import (
    EmptyParameterValue,
)
from openapi_core.exceptions import OpenAPIError as CoreOpenAPIError
from openapi_core.schema.media_types.exceptions import (
    InvalidContentType,
    OpenAPIMediaTypeError,
)
from openapi_core.schema.parameters.exceptions import (
    MissingParameter,
    MissingRequiredParameter,
    OpenAPIParameterError,
)
from openapi_core.schema.responses.exceptions import InvalidResponse
from openapi_core.unmarshalling.schemas.exceptions import (
    InvalidSchemaValue,
    UnmarshalError,
)
from openapi_core.validation.exceptions import InvalidSecurity

from ..annotations import DictStrAny, MappingStrStr, TypedDict


ERROR_FIELD_REQUIRED = "Field required"
ERROR_NOT_FOUND_TEMPLATE = "{label} not found"
ERROR_PARAMETER_EMPTY = "Empty parameter value"
ERROR_PARAMETER_INVALID = "Invalid parameter value"
ERROR_PARAMETER_MISSING = "Missing parameter"
ERROR_PARAMETER_REQUIRED = "Parameter required"
OBJECT_LABEL = "Object"

PathItem = Union[int, str]
DictPathItemAny = Dict[PathItem, Any]

logger = logging.getLogger(__name__)
required_message_re = re.compile(
    r"^'(?P<field_name>.*)' is a required property$"
)


@attr.s(hash=True)
class CastError(CoreCastError):
    name: str = attr.ib()
    value: str = attr.ib()
    type: str = attr.ib()  # noqa: A003, VNE003


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


class BadRequest(OpenAPIError):
    """Bad request basic error."""

    default_message = "Bad request"
    status = 400


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
    """Request / response validation error.

    There is an ability to wrap ``openapi-core`` request / response validation
    errors via :func:`.from_request_errors` class method as in same time to
    create a validation error from the dict, like:

    .. code-block:: python

        raise ValidationError.from_dict(
            body={"name": "Name is not unique"}
        )
        raise ValidationError.from_dict(
            parameters={"X-Api-Key": "Outdated API key"}
        )
        raise ValidationError.from_dict(
            body={
                0: {
                    "data": {
                        0: {"name": "Field required"},
                        1: {"description": "Field required"},
                    },
                },
            },
        )

    Given interface is recommended for end users, who want to raise a
    custom validation errors within their operation handlers.
    """

    default_message = "Validation error"
    status = 422

    def __init__(
        self, *, message: str = None, errors: List[ValidationErrorItem] = None,
    ) -> None:
        super().__init__(message or self.default_message)

        self.errors = errors
        self.data = {"detail": errors} if errors else None

    @classmethod
    def from_dict(  # type: ignore
        cls, data: DictPathItemAny = None, **kwargs: Any
    ) -> "ValidationError":
        if data and kwargs:
            raise ValueError(
                "Please supply only data dict or kwargs, not both"
            )

        def dict_walker(
            loc: List[PathItem],
            data: Union[DictPathItemAny, DictStrAny],
            errors: List[ValidationErrorItem],
        ) -> None:
            for key, value in data.items():
                if isinstance(value, dict):
                    dict_walker(loc + [key], value, errors)
                else:
                    errors.append({"loc": loc + [key], "message": value})

        errors: List[ValidationErrorItem] = []
        dict_walker([], data or kwargs, errors)
        return cls(errors=errors)

    @classmethod
    def from_request_errors(  # type: ignore
        cls,
        errors: List[CoreOpenAPIError],
        *,
        base_loc: List[PathItem] = None,
    ) -> "ValidationError":
        base_loc = ["body"] if base_loc is None else base_loc
        result = []

        for err in errors:
            if isinstance(err, (OpenAPIParameterError, EmptyParameterValue)):
                result.append(get_parameter_error_details(base_loc, err))
            elif isinstance(err, OpenAPIMediaTypeError):
                result.append(get_media_type_error_details(base_loc, err))
            elif isinstance(err, CastError):
                result.append(
                    {
                        "loc": [*base_loc, err.name],
                        "message": (
                            f"{err.value!r} is not a type of {err.type!r}"
                        ),
                    }
                )
            elif isinstance(err, UnmarshalError):
                result.extend(get_unmarshal_error_details(base_loc, err))
            else:
                result.append(get_common_error_details(base_loc, err))

        return cls(
            message="Request parameters or body validation error",
            errors=result,
        )

    @classmethod
    def from_response_errors(  # type: ignore
        cls, errors: List[CoreOpenAPIError]
    ) -> "ValidationError":
        result: List[ValidationErrorItem] = []
        loc: List[PathItem] = ["response"]

        for err in errors:
            if isinstance(err, InvalidResponse):
                available_responses = ", ".join(sorted(err.responses))
                result.append(
                    {
                        "loc": loc,
                        "message": (
                            f"{err}. Available response http statuses: "
                            f"{available_responses}"
                        ),
                    }
                )
            elif isinstance(err, OpenAPIMediaTypeError):
                result.append(get_media_type_error_details(loc, err))
            elif isinstance(err, UnmarshalError):
                result.extend(get_unmarshal_error_details(loc, err))
            else:
                result.append(get_common_error_details(loc, err))

        return cls(message="Response data validation error", errors=result)


def ensure_loc(loc: List[PathItem]) -> List[PathItem]:
    return [item for item in loc if item != ""]


def get_common_error_details(
    loc: List[PathItem], err: CoreOpenAPIError
) -> ValidationErrorItem:
    return {"loc": loc, "message": str(err)}


def get_json_schema_validation_error_details(
    loc: List[PathItem], err: JsonSchemaValidationError
) -> ValidationErrorItem:
    message = err.message
    path = list(err.absolute_path)
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
        "message": err.message,
    }


def get_media_type_error_details(
    loc: List[PathItem], err: OpenAPIMediaTypeError
) -> ValidationErrorItem:
    if isinstance(err, InvalidContentType):
        return {
            "loc": loc,
            "message": (
                f"Schema missing for following mimetype: {err.mimetype}"
            ),
        }

    return get_common_error_details(loc, err)


def get_parameter_error_details(
    loc: List[PathItem], err: OpenAPIParameterError,
) -> ValidationErrorItem:
    parameter_name: str = getattr(err, "name", None)
    if parameter_name is None:
        return get_common_error_details(loc, err)

    message = {
        DeserializeError: ERROR_PARAMETER_INVALID,
        EmptyParameterValue: ERROR_PARAMETER_EMPTY,
        MissingParameter: ERROR_PARAMETER_MISSING,
        MissingRequiredParameter: ERROR_PARAMETER_REQUIRED,
    }[type(err)]

    return {"loc": [*loc, parameter_name], "message": message}


def get_unmarshal_error_details(
    loc: List[PathItem], err: UnmarshalError
) -> List[ValidationErrorItem]:
    if isinstance(err, InvalidSchemaValue):
        return [
            get_json_schema_validation_error_details(loc, item)
            for item in err.schema_errors
        ]

    return [get_common_error_details(loc, err)]


def is_only_security_error(errors: List[CoreOpenAPIError]) -> bool:
    return len(errors) == 1 and isinstance(errors[0], InvalidSecurity)
