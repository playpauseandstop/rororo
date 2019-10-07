import json
from pathlib import Path
from typing import overload, Union

import yaml
from aiohttp import web

from . import views
from .constants import OPENAPI_SCHEMA_APP_KEY
from .decorators import openapi_operation
from .exceptions import ConfigurationError, OperationError
from .utils import (
    get_operation_details,
    guess_openapi_schema_path,
    safe_route_name,
)
from ..annotations import Decorator, DictStrAny, Handler


class OperationRegistrator:
    def __init__(self, operations: "OperationTableDef") -> None:
        self.operations = operations

    @overload
    def __call__(self, handler: Handler) -> Handler:
        ...

    @overload  # noqa: F811
    def __call__(self, operation_id: str) -> Decorator:
        ...

    def __call__(self, mixed):  # type: ignore  # noqa: F811
        operation_id = mixed if isinstance(mixed, str) else mixed.__name__

        def decorator(handler: Handler) -> Handler:
            openapi_handler = openapi_operation(operation_id)(handler)

            self.operations[operation_id] = openapi_handler
            return openapi_handler

        return decorator(mixed) if callable(mixed) else decorator


class OperationTableDef(dict):
    def __init__(self) -> None:
        self.register = OperationRegistrator(self)


def convert_operations_to_routes(
    operations: OperationTableDef, schema: DictStrAny
) -> web.RouteTableDef:
    routes = web.RouteTableDef()

    for operation_id, handler in operations.items():
        details = get_operation_details(schema, operation_id)
        if details is None:
            raise OperationError(
                f"Operation ID {operation_id} not found in provided OpenAPI "
                "Schema."
            )

        routes.route(
            details.method, details.path, name=safe_route_name(operation_id)
        )(handler)

    return routes


def setup_openapi(
    app: web.Application,
    schema_path: Union[str, Path],
    *operations: OperationTableDef,
) -> None:
    def read_schema(path: Path) -> DictStrAny:
        content = path.read_text()
        if path.suffix == ".json":
            return json.loads(content)

        if path.suffix in {".yml", ".yaml"}:
            return yaml.safe_load(content)

        raise ConfigurationError(
            f"Unsupported OpenAPI schema file: {path.name}. At a moment "
            "rororo supports loading OpenAPI schemas from: .json, .yml, .yaml"
        )

    path = Path(schema_path) if isinstance(schema_path, str) else schema_path
    if not path.exists() or not path.is_file():
        raise ConfigurationError(
            f"Unable to find OpenAPI schema file at {path}"
        )

    app[OPENAPI_SCHEMA_APP_KEY] = schema = read_schema(path)
    for item in operations:
        app.router.add_routes(convert_operations_to_routes(item, schema))

    app.router.add_get(guess_openapi_schema_path(schema), views.openapi_schema)
