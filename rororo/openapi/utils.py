from typing import Optional, Union

from aiohttp import web
from aiohttp.helpers import ChainMapProxy
from openapi_core.schema.specs.models import Spec

from .constants import (
    OPENAPI_CONTEXT_REQUEST_KEY,
    OPENAPI_SCHEMA_APP_KEY,
    OPENAPI_SPEC_APP_KEY,
)
from .data import OpenAPIContext, OpenAPIOperation
from .exceptions import ConfigurationError, ContextError, OperationError
from ..annotations import DictStrAny


def add_prefix(path: str, prefix: Optional[str]) -> str:
    return f"{prefix}{path}" if prefix else path


def get_openapi_context(request: web.Request) -> OpenAPIContext:
    """Shortcut to retrieve OpenAPI schema from ``aiohttp.web`` request.

    ``OpenAPIContext`` attached to :class:`aiohttp.web.Request` instance only
    if current request contains valid data.

    ``ContextError`` raises if, for some reason, the function called outside of
    valid OpenAPI request context.
    """
    try:
        return request[OPENAPI_CONTEXT_REQUEST_KEY]
    except KeyError:
        raise ContextError(
            "Request instance does not contain valid OpenAPI context. In "
            "most cases it means, the function is called outside of valid "
            "OpenAPI request context."
        )


def get_openapi_schema(
    mixed: Union[web.Application, ChainMapProxy]
) -> DictStrAny:
    """Shortcut to retrieve OpenAPI schema from ``aiohttp.web`` application.

    ``ConfigruationError`` raises if :class:`aiohttp.web.Application` does not
    contain registered OpenAPI schema.
    """
    try:
        return mixed[OPENAPI_SCHEMA_APP_KEY]
    except KeyError:
        raise ConfigurationError(
            "Seems like OpenAPI schema not registered to the application. Use "
            '"from rororo import setup_openapi" function to register OpenAPI '
            "schema to your web.Application."
        )


def get_openapi_spec(mixed: Union[web.Application, ChainMapProxy]) -> Spec:
    """Shortcut to retrieve OpenAPI spec from ``aiohttp.web`` application.

    ``ConfigruationError`` raises if :class:`aiohttp.web.Application` does not
    contain registered OpenAPI spec.
    """
    try:
        return mixed[OPENAPI_SPEC_APP_KEY]
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
