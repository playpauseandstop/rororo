class OpenAPIError(Exception):
    """Base exception for other OpenAPI exceptions."""


class ConfigurationError(OpenAPIError):
    """Wrong OpenAPI configuration."""


class OperationError(OpenAPIError):
    """Invalid OpenAPI operation."""


class ParameterError(OpenAPIError):
    """OpenAPI parameter error."""


class RequestBodyError(OpenAPIError):
    """Request body error."""


class ValidationError(OpenAPIError):
    """Validation error."""
