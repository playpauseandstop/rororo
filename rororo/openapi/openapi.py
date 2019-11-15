import json
import os
from pathlib import Path
from typing import Dict, overload, Union

import yaml
from aiohttp import web
from openapi_core.shortcuts import create_spec
from openapi_spec_validator.exceptions import OpenAPIValidationError

from . import views
from .constants import (
    OPENAPI_IS_VALIDATE_RESPONSE_APP_KEY,
    OPENAPI_SCHEMA_APP_KEY,
    OPENAPI_SPEC_APP_KEY,
)
from .decorators import openapi_operation
from .exceptions import ConfigurationError
from .utils import add_prefix, get_openapi_operation
from ..annotations import Decorator, DictStrAny, Handler


class OperationRegistrator:
    def __init__(self, operations: "OperationTableDef") -> None:
        self.operations = operations

    @overload
    def __call__(self, handler: Handler) -> Handler:
        ...  # pragma: no cover

    @overload  # noqa: F811
    def __call__(self, operation_id: str) -> Decorator:  # noqa: F811
        ...  # pragma: no cover

    def __call__(self, mixed):  # type: ignore  # noqa: F811
        operation_id = mixed if isinstance(mixed, str) else mixed.__name__

        def decorator(handler: Handler) -> Handler:
            openapi_handler = openapi_operation(operation_id)(handler)

            self.operations[operation_id] = openapi_handler
            return openapi_handler

        return decorator(mixed) if callable(mixed) else decorator


class OperationTableDef(Dict[str, Handler]):
    """Map OpenAPI 3 operations to aiohttp.web view handlers.

    In short it is rororo's equialent to :class:`aiohttp.web.RouteTableDef`.
    Under the hood, on :func:`rororo.openapi.setup_openapi` it
    still will use ``RouteTableDef`` for registering view handlers to
    :class:`aiohttp.web.Application`.

    But unlike ``RouteTableDef`` it does not register any HTTP method handlers
    (as via ``@routes.get`` decorator) in favor of just registering the
    operations.

    There are two ways for registering view hanlder,

    1. With bare ``@operations.register`` call when OpenAPI ``operationId``
       equals to view handler name.
    2. Or by passing ``operation_id`` to the decorator as first arg, when
       ``operationId`` does not match view handler name, or if you don't like
       the fact of guessing operation ID from view handler name.

    Both of ways described below,

    .. code-block:: python

        from rororo import OperationTableDef

        operations = OperationTableDef()

        # Expect OpenAPI 3 schema to contain operationId: hello_world
        @operations.register
        async def hello_world(request: web.Request) -> web.Response:
            ...

        # Explicitly use operationId: helloWorld
        @operations.register("helloWorld")
        async def hello_world(request: web.Request) -> web.Response:
            ...

    If supplied ``operation_id`` does not exist in OpenAPI 3 schema,
    :func:`rororo.openapi.setup_openapi` call raises an ``OperationError``.
    """

    def __init__(self) -> None:
        self.register = OperationRegistrator(self)


def convert_operations_to_routes(
    operations: OperationTableDef, oas: DictStrAny, *, prefix: str = None
) -> web.RouteTableDef:
    """Convert operations table defintion to routes table definition."""
    routes = web.RouteTableDef()

    for operation_id, handler in operations.items():
        operation = get_openapi_operation(oas, operation_id)
        routes.route(
            operation.method,
            add_prefix(operation.path, prefix),
            name=operation.route_name,
        )(handler)

    return routes


def setup_openapi(
    app: web.Application,
    schema_path: Union[str, Path],
    *operations: OperationTableDef,
    route_prefix: str = None,
    is_validate_response: bool = False,
    has_openapi_schema_handler: bool = True,
) -> None:
    """Setup OpenAPI schema to use with aiohttp.web application.

    Unlike `aiohttp-apispec <https://aiohttp-apispec.readthedocs.io/>`_ and
    other tools, which provides OpenAPI/Swagger support for aiohttp.web
    applications, ``rororo`` changes the way of using OpenAPI schema with
    ``aiohttp.web`` apps.

    ``rororo`` relies on concrete OpenAPI schema file, path to which need to be
    registered on application startup (mostly inside of ``create_app`` factory
    or right after :class:`aiohttp.web.Application` instantiation).

    And as valid OpenAPI schema ensure unique ``operationId`` used accross the
    schema ``rororo`` uses them as a key while telling aiohttp.web to use given
    view handler for serving required operation.

    With that in mind registering (setting up) OpenAPI schema requires:

    1. :class:`aiohttp.web.Application` instance
    2. Path to file (json or yaml) with OpenAPI schema
    3. OpenAPI operation handlers mapping (rororo's equialent of
       :class:`aiohttp.web.RouteTableDef`)

    In common cases setup looks like,

    .. code-block:: python

        from pathlib import Path
        from typing import List

        from aiohttp import web

        from .views import operations


        def create_app(argv: List[str] = None) -> web.Application:
            app = web.Application()
            setup_openapi(
                app,
                Path(__file__).parent / 'openapi.yaml',
                operations
            )
            return app

    It is also possible to setup route prefix to use if server URL inside of
    your OpenAPI schema ends with path, like ``http://yourserver.url/api``.
    For that cases you need to pass ``'/api'`` as a ``route_prefix`` keyword
    argument.

    By default, ``rororo`` will not validate operation responses against
    OpenAPI schema due to performance reasons. To enable this feature, pass
    ``is_validate_response`` truthy flag.

    By default, ``rororo`` will share the OpenAPI schema which is registered
    for your aiohttp.web application. In case if you don't want to share this
    schema, pass ``has_openapi_schema_handler=False`` on setting up OpenAPI.
    """

    def read_schema(path: Path) -> DictStrAny:
        content = path.read_text()
        if path.suffix == ".json":
            return json.loads(content)

        if path.suffix in {".yml", ".yaml"}:
            return yaml.safe_load(content)

        raise ConfigurationError(
            f"Unsupported OpenAPI schema file: {path}. At a moment rororo "
            "supports loading OpenAPI schemas from: .json, .yml, .yaml files"
        )

    # Ensure OpenAPI schema is a readable file
    path = Path(schema_path) if isinstance(schema_path, str) else schema_path
    if not path.exists() or not path.is_file():
        uid = os.getuid()
        raise ConfigurationError(
            f"Unable to find OpenAPI schema file at {path}. Please check that "
            "file exists at given path and readable by current user ID: "
            f"{uid}"
        )

    # Store OpenAPI schema dict in the application dict
    app[OPENAPI_SCHEMA_APP_KEY] = oas = read_schema(path)

    # Create the spec and put it to the application dict as well
    try:
        app[OPENAPI_SPEC_APP_KEY] = create_spec(oas)
    except OpenAPIValidationError:
        raise ConfigurationError(
            f"Unable to load valid OpenAPI schema in {path}. In most cases "
            "it means that given file doesn't contain valid OpenAPI 3 schema. "
            "To get full details about errors run `openapi-spec-validator "
            f"{path}`"
        )

    # Store whether rororo need to validate response or not. By default: not
    app[OPENAPI_IS_VALIDATE_RESPONSE_APP_KEY] = is_validate_response

    # Register all operation handlers to web application
    for item in operations:
        app.router.add_routes(
            convert_operations_to_routes(item, oas, prefix=route_prefix)
        )

    # Register the route to dump openapi schema used for the application if
    # required
    if has_openapi_schema_handler:
        app.router.add_get(
            add_prefix("/openapi.{schema_format}", route_prefix),
            views.openapi_schema,
        )
