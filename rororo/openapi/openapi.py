import json
import os
from pathlib import Path
from typing import Dict, overload, Union

import yaml
from aiohttp import web
from aiohttp_middlewares import cors_middleware, error_middleware
from openapi_core.shortcuts import create_spec
from openapi_spec_validator.exceptions import OpenAPIValidationError
from yarl import URL

from . import views
from .constants import (
    APP_OPENAPI_IS_VALIDATE_RESPONSE_KEY,
    APP_OPENAPI_SCHEMA_KEY,
    APP_OPENAPI_SPEC_KEY,
)
from .decorators import openapi_operation
from .exceptions import ConfigurationError
from .utils import add_prefix, get_openapi_operation
from ..annotations import Decorator, DictStrAny, Handler
from ..settings import APP_SETTINGS_KEY, BaseSettings


Url = Union[str, URL]


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

    @overload
    def register(self, handler: Handler) -> Handler:
        ...  # pragma: no cover

    @overload
    def register(self, operation_id: str) -> Decorator:  # noqa: F811
        ...  # pragma: no cover

    def register(self, mixed):  # type: ignore  # noqa: F811
        operation_id = mixed if isinstance(mixed, str) else mixed.__name__

        def decorator(handler: Handler) -> Handler:
            openapi_handler = openapi_operation(operation_id)(handler)

            self[operation_id] = openapi_handler
            return openapi_handler

        return decorator(mixed) if callable(mixed) else decorator


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


def find_route_prefix(
    oas: DictStrAny,
    *,
    server_url: Union[str, URL] = None,
    settings: BaseSettings = None,
) -> str:
    if server_url is not None:
        return get_route_prefix(server_url)

    servers = oas["servers"]
    if len(servers) == 1:
        return get_route_prefix(servers[0]["url"])

    if settings is None:
        raise ConfigurationError(
            "Unable to guess route prefix as OpenAPI schema contains "
            "multiple servers and aiohttp.web has no settings instance "
            "configured."
        )

    for server in servers:
        mixed = server.get("x-rororo-level")
        if isinstance(mixed, list):
            if settings.level in mixed:
                return get_route_prefix(server["url"])
        elif mixed == settings.level:
            return get_route_prefix(server["url"])

    raise ConfigurationError(
        "Unable to guess route prefix as no server in OpenAPI schema has "
        f'defined "x-rororo-level" key of "{settings.level}".'
    )


def get_route_prefix(mixed: Url) -> str:
    return (URL(mixed) if isinstance(mixed, str) else mixed).path


def setup_openapi(
    app: web.Application,
    schema_path: Union[str, Path],
    *operations: OperationTableDef,
    server_url: Url = None,
    is_validate_response: bool = True,
    has_openapi_schema_handler: bool = True,
    use_error_middleware: bool = True,
    use_cors_middleware: bool = True,
    cors_middleware_kwargs: DictStrAny = None,
) -> web.Application:
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
            return setup_openapi(
                web.Application(),
                Path(__file__).parent / "openapi.yaml",
                operations,
            )

    If your OpenAPI schema contains multiple servers schemas, like,

    .. code-block:: yaml

        servers:
        - url: "/api/"
          description: "Test environment"
        - url: "http://localhost:8080/api/"
          description: "Dev environment"
        - url: "http://prod.url/api/"
          description: "Prod environment"

    you have 2 options of telling ``rororo`` to use specific server URL.

    First, is passing ``server_url``, while setting up OpenAPI, for example,

    .. code-block:: python

        setup_openapi(
            web.Application(),
            Path(__file__).parent / "openapi.yaml",
            operations,
            server_url=URL("http://prod.url/api/"),
        )

    Second, is more complicated as you need to wrap ``aiohttp.web`` application
    into :func:`rororo.settings.setup_settings` and mark each server with
    ``x-rororo-level`` special key in server schema definition as,

    .. code-block:: yaml

        servers:
        - url: "/api/"
          x-rororo-level: "test"
        - url: "http://localhost:8080/api/"
          x-rororo-level: "dev"
        - url: "http://prod.url/api/"
          x-rororo-level: "prod"

    After, ``rororo`` will try to equal current app settings level with the
    schema and if URL matched, will use given server URL for finding out
    route prefix.

    By default, ``rororo`` will validate operation responses against OpenAPI
    schema. To disable this feature, pass ``is_validate_response`` falsy flag.

    By default, ``rororo`` will share the OpenAPI schema which is registered
    for your aiohttp.web application. In case if you don't want to share this
    schema, pass ``has_openapi_schema_handler=False`` on setting up OpenAPI.

    By default, ``rororo`` will enable
    :func:`aiohttp_middlewares.cors.cors_middleware` without any settings and
    :func:`aiohttp_middlewares.error.error_middleware` with custom error
    handler to ensure that security / validation errors does not provide any
    mess to command line. Pass ``use_cors_middleware`` /
    ``use_error_middleware`` to change or entirely disable this default
    behaviour.

    For passing custom options to CORS middleware, use
    ``cors_middleware_kwargs`` mapping. If kwarg does not support by CORS
    middleware - ``rororo`` will raise a ``ConfigurationError``. All list of
    options available at documentation for
    :func:`aiohttp_middlewares.cors.cors_middleware`.
    """

    def read_schema(path: Path) -> DictStrAny:
        content = path.read_text()
        if path.suffix == ".json":
            return json.loads(content)  # type: ignore

        if path.suffix in {".yml", ".yaml"}:
            return yaml.safe_load(content)  # type: ignore

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
    app[APP_OPENAPI_SCHEMA_KEY] = oas = read_schema(path)

    # Create the spec and put it to the application dict as well
    try:
        app[APP_OPENAPI_SPEC_KEY] = create_spec(oas)
    except OpenAPIValidationError:
        raise ConfigurationError(
            f"Unable to load valid OpenAPI schema in {path}. In most cases "
            "it means that given file doesn't contain valid OpenAPI 3 schema. "
            "To get full details about errors run `openapi-spec-validator "
            f"{path}`"
        )

    # Store whether rororo need to validate response or not. By default: not
    app[APP_OPENAPI_IS_VALIDATE_RESPONSE_KEY] = is_validate_response

    # Register all operation handlers to web application
    route_prefix = find_route_prefix(
        oas, server_url=server_url, settings=app.get(APP_SETTINGS_KEY)
    )
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

    # Add error middleware if necessary
    if use_error_middleware:
        app.middlewares.insert(
            0, error_middleware(default_handler=views.default_error_handler)
        )

    # Add CORS middleware if necessary
    if use_cors_middleware:
        try:
            app.middlewares.insert(
                0, cors_middleware(**(cors_middleware_kwargs or {}))
            )
        except TypeError:
            raise ConfigurationError(
                "Unsupported kwargs passed to CORS middleware. Please check "
                "given kwargs and remove unsupported ones: "
                "{cors_middleware_kwargs!r}"
            )

    return app
