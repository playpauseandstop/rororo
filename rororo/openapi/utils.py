import types
from typing import Optional

import attr
from aiohttp import web

from .constants import OPENAPI_SCHEMA_APP_KEY
from ..annotations import DictStrAny, MappingStrAny


@attr.dataclass(frozen=True, slots=True)
class OperationDetails:
    method: str
    path: str


def get_openapi_schema(app: web.Application) -> DictStrAny:
    """Shortcut to retrieve OpenAPI schema from ``aiohttp.web`` application."""
    return app[OPENAPI_SCHEMA_APP_KEY]


def get_operation_details(
    schema: DictStrAny, operation_id: str
) -> Optional[OperationDetails]:
    """Go through OpenAPI schema and try to find operation details by its ID.

    These details allow to add given operation to router as they share:

    - method
    - path

    for the operation.
    """
    for path, path_schema in (schema.get("paths") or {}).items():
        for method, operation_schema in path_schema.items():
            if operation_schema.get("operationId") == operation_id:
                return OperationDetails(method=method, path=path)
    return None


def guess_openapi_schema_path(schema: DictStrAny) -> str:
    return "/api/openapi.{schema_format}"


def immutable_dict_factory() -> MappingStrAny:
    """Shortcut to create immutable dict factory.

    For now, stick with ``types.MappingProxyType`` as immutable dict
    implementation.
    """
    return types.MappingProxyType({})


def safe_route_name(operation_id: str) -> str:
    """Ensure safe route name for given operation ID.

    OpenAPI schema allows to use spaces for operation ID, while aiohttp
    disallows them. Cause of that replace all spaces with dashes.
    """
    return operation_id.replace(" ", "-")
