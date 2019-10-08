from typing import Optional

from aiohttp import web

from .constants import OPENAPI_SCHEMA_APP_KEY, OPENAPI_SPEC_APP_KEY
from .data import OpenAPIOperation
from .exceptions import ConfigurationError, OperationError
from ..annotations import DictStrAny


def add_prefix(path: str, prefix: Optional[str]) -> str:
    return f"{prefix}{path}" if prefix else path


def get_openapi_schema(app: web.Application) -> DictStrAny:
    """Shortcut to retrieve OpenAPI schema from ``aiohttp.web`` application."""
    try:
        return app[OPENAPI_SCHEMA_APP_KEY]
    except KeyError:
        raise ConfigurationError(
            "Seems like OpenAPI schema not registered to the application. Use "
            '"from rororo import setup_openapi" function to register OpenAPI '
            "schema to your web.Application."
        )


def get_openapi_spec(app: web.Application) -> DictStrAny:
    """Shortcut to retrieve OpenAPI spec from ``aiohttp.web`` application."""
    try:
        return app[OPENAPI_SPEC_APP_KEY]
    except KeyError:
        raise ConfigurationError(
            "Seems like OpenAPI spec not registered to the application. Use "
            '"from rororo import setup_openapi" function to register OpenAPI '
            "schema to your web.Application."
        )


def get_openapi_operation(
    oas: DictStrAny, operation_id: str
) -> OpenAPIOperation:
    """Go through OpenAPI schema and try to find operation details by its ID.

    These details allow to add given operation to router as they share:

    - method
    - path

    for the operation.
    """
    for path, path_schema in (oas.get("paths") or {}).items():
        for method, operation_schema in path_schema.items():
            if operation_schema.get("operationId") == operation_id:
                return OpenAPIOperation(
                    id=operation_id,
                    method=method,
                    path=path,
                    schema=operation_schema,
                )

    raise OperationError(
        f'Unable to find operation "{operation_id}" in provided OpenAPI '
        "Schema."
    )
