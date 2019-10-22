class OpenAPIError(Exception):
    """Base exception for other OpenAPI exceptions."""


class ConfigurationError(OpenAPIError):
    """Wrong OpenAPI configuration."""


class ContextError(OpenAPIError):
    """Attempt to use context when it is not available."""


class OperationError(OpenAPIError):
    """Invalid OpenAPI operation."""


class SecurityError(OpenAPIError):
    """Request is not secured, but should."""
