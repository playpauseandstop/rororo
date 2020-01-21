from ..annotations import MappingStrStr


NOT_FOUND_TEMPLATE = "{label} not found"
OBJECT_LABEL = "Object"
VALIDATION_ERROR_TEMPLATE = "{label} validation error"


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

    default_message = NOT_FOUND_TEMPLATE.format(label=OBJECT_LABEL)
    status = 404

    def __init__(
        self, label: str = OBJECT_LABEL, *, headers: MappingStrStr = None
    ) -> None:
        super().__init__(
            NOT_FOUND_TEMPLATE.format(label=label), headers=headers,
        )
        self.label = label


class ValidationError(OpenAPIError):
    """OpenAPI request / response validation error."""

    default_message = "Validation error"
    status = 422

    def __init__(self, label: str = None, **data: str) -> None:
        if label:
            message = VALIDATION_ERROR_TEMPLATE.format(label=label)
        else:
            message = self.default_message

        super().__init__(message)
        self.data = {
            "detail": [
                {"loc": key.split("."), "message": value}
                for key, value in data.items()
            ]
        }
