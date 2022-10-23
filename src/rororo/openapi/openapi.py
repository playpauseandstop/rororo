import inspect
import json
import os
import warnings
from functools import lru_cache, partial
from pathlib import Path
from typing import Callable, cast, Deque, Dict, List, overload, Tuple, Union

import attr
import yaml
from aiohttp import hdrs, web
from aiohttp_middlewares import cors_middleware
from openapi_core.schema.specs.models import Spec
from openapi_core.shortcuts import create_spec
from pyrsistent import pmap
from yarl import URL

from rororo.annotations import (
    DictStrAny,
    DictStrStr,
    F,
    Handler,
    Protocol,
    ViewType,
)
from rororo.openapi import views
from rororo.openapi.annotations import (
    CorsMiddlewareKwargsDict,
    ErrorMiddlewareKwargsDict,
    SecurityDict,
    ValidateEmailKwargsDict,
)
from rororo.openapi.constants import (
    APP_OPENAPI_SCHEMA_KEY,
    APP_OPENAPI_SPEC_KEY,
    APP_VALIDATE_EMAIL_KWARGS_KEY,
    HANDLER_OPENAPI_MAPPING_KEY,
)
from rororo.openapi.core_data import get_core_operation
from rororo.openapi.exceptions import ConfigurationError
from rororo.openapi.middlewares import openapi_middleware
from rororo.openapi.utils import add_prefix
from rororo.settings import APP_SETTINGS_KEY, BaseSettings


SchemaLoader = Callable[[bytes], DictStrAny]
Url = Union[str, URL]


class CreateSchemaAndSpec(Protocol):
    def __call__(
        self, path: Path, *, schema_loader: Union[SchemaLoader, None] = None
    ) -> Tuple[DictStrAny, Spec]:  # pragma: no cover
        ...


@attr.dataclass(slots=True)
class OperationTableDef:
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


        # Explicitly use `operationId: "helloWorld"`
        @operations.register("helloWorld")
        async def hello_world(request: web.Request) -> web.Response:
            ...

    Class based views supported as well. In most generic way you just need
    to decorate your view with ``@operations.register`` decorator and ensure
    that ``operationId`` equals to view method qualified name
    (``__qualname__``).

    For example,

    .. code-block:: python

        @operations.register
        class UserView(web.View):
            async def get(self) -> web.Response:
                ...

    expects for operation ID ``UserView.get`` to be declared in OpenAPI schema.

    In same time,

    .. code-block:: python

        @operations.register("users")
        class UserView(web.View):
            async def get(self) -> web.Response:
                ...

    expects for operation ID ``users.get`` to be declared in OpenAPI schema.

    Finally,

    .. code-block:: python

        @operations.register
        class UserView(web.View):
            @operations.register("me")
            async def get(self) -> web.Response:
                ...

    expects for operation ID ``me`` to be declared in OpenAPI schema.

    When the class based view provides mutliple view methods (for example
    ``delete``, ``get``, ``patch`` & ``put``) *rororo* expects that
    OpenAPI schema contains operation IDs for each of view method.

    If supplied ``operation_id`` does not exist in OpenAPI 3 schema,
    :func:`rororo.openapi.setup_openapi` call raises an ``OperationError``.
    """

    handlers: List[Handler] = attr.Factory(list)
    views: List[ViewType] = attr.Factory(list)

    def __add__(self, other: "OperationTableDef") -> "OperationTableDef":
        return OperationTableDef(
            handlers=[*self.handlers, *other.handlers],
            views=[*self.views, *other.views],
        )

    def __iadd__(self, other: "OperationTableDef") -> "OperationTableDef":
        self.handlers.extend(other.handlers)
        self.views.extend(other.views)
        return self

    @overload
    def register(self, handler: F) -> F:
        ...

    @overload
    def register(self, operation_id: str) -> Callable[[F], F]:
        ...

    def register(self, mixed):  # type: ignore[no-untyped-def]
        operation_id = mixed if isinstance(mixed, str) else mixed.__qualname__

        def decorator(handler: F) -> F:
            mapping: DictStrStr = {}

            if self._is_view(handler):
                mapping.update(
                    self._register_view(handler, operation_id)  # type: ignore[arg-type]
                )
            else:
                mapping.update(self._register_handler(handler, operation_id))

            setattr(handler, HANDLER_OPENAPI_MAPPING_KEY, pmap(mapping))
            return handler

        return decorator(mixed) if callable(mixed) else decorator

    def _is_view(self, handler: F) -> bool:
        return inspect.isclass(handler) and issubclass(handler, web.View)

    def _register_handler(
        self, handler: Handler, operation_id: str
    ) -> DictStrStr:
        # Hacky way to check whether handler is a view function or view method
        has_self_parameter = "self" in inspect.signature(handler).parameters

        # Register only view functions, view methods will be registered via
        # view class instead
        if not has_self_parameter:
            self.handlers.append(handler)

        return {hdrs.METH_ANY: operation_id}

    def _register_view(self, view: ViewType, prefix: str) -> DictStrStr:
        mapping: DictStrStr = {}

        for value in vars(view).values():
            if not callable(value):
                continue

            name = value.__name__
            maybe_method = name.upper()
            if maybe_method not in hdrs.METH_ALL:
                continue

            maybe_operation_id = getattr(
                value, HANDLER_OPENAPI_MAPPING_KEY, {}
            ).get(hdrs.METH_ANY)
            mapping[maybe_method] = (
                maybe_operation_id
                if maybe_operation_id
                else f"{prefix}.{name}"
            )

        self.views.append(view)
        return mapping


def convert_operations_to_routes(
    operations: OperationTableDef,
    spec: Spec,
    *,
    prefix: Union[str, None] = None,
) -> web.RouteTableDef:
    """Convert operations table defintion to routes table definition."""

    async def noop(request: web.Request) -> web.Response:
        return web.json_response(status=204)  # pragma: no cover

    routes = web.RouteTableDef()

    # Add plain handlers to the route table def as a route
    for handler in operations.handlers:
        operation_id = getattr(handler, HANDLER_OPENAPI_MAPPING_KEY)[
            hdrs.METH_ANY
        ]
        core_operation = get_core_operation(spec, operation_id)

        routes.route(
            core_operation.http_method,
            add_prefix(core_operation.path_name, prefix),
            name=get_route_name(core_operation.operation_id),
        )(handler)

    # But view should be added as a view instead
    for view in operations.views:
        ids: Deque[str] = Deque(
            getattr(view, HANDLER_OPENAPI_MAPPING_KEY).values()
        )

        first_operation_id = ids.popleft()
        core_operation = get_core_operation(spec, first_operation_id)

        path = add_prefix(core_operation.path_name, prefix)
        routes.view(
            path,
            name=get_route_name(core_operation.operation_id),
        )(view)

        # Hacky way of adding aliases to class based views with multiple
        # registered view methods
        for other_operation_id in ids:
            routes.route(
                hdrs.METH_ANY, path, name=get_route_name(other_operation_id)
            )(noop)

    return routes


def create_schema_and_spec(
    path: Path, *, schema_loader: Union[SchemaLoader, None] = None
) -> Tuple[DictStrAny, Spec]:
    schema = read_openapi_schema(path, loader=schema_loader)
    return (schema, create_spec(schema))


@lru_cache(maxsize=128)
def create_schema_and_spec_with_cache(  # type: ignore[misc]
    path: Path, *, schema_loader: Union[SchemaLoader, None] = None
) -> Tuple[DictStrAny, Spec]:
    return create_schema_and_spec(path, schema_loader=schema_loader)


def find_route_prefix(
    oas: DictStrAny,
    *,
    server_url: Union[Url, None] = None,
    settings: Union[BaseSettings, None] = None,
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


def fix_spec_operations(spec: Spec, schema: DictStrAny) -> Spec:
    """Fix spec operations.

    ``openapi-core`` sets up operation security to an empty list even it is
    not defined within the operation schema. This function fixes this behaviour
    by reading schema first and if operation schema misses ``security``
    definition - sets up a ``None`` as an operation security.

    This allows properly distinct empty operation security and missed operation
    security. With empty operation security (empty list) - mark an operation
    as unsecured. With missed operation security - use global security schema
    if it is defined.
    """
    mapping: Dict[str, Union[SecurityDict, None]] = {}

    for path_data in schema["paths"].values():
        for maybe_operation_data in path_data.values():
            if not isinstance(maybe_operation_data, dict):
                continue

            operation_id = maybe_operation_data.get("operationId")
            if operation_id is None:
                continue

            mapping[operation_id] = maybe_operation_data.get("security")

    for path in spec.paths.values():
        for operation in path.operations.values():
            if operation.security != []:
                continue

            if operation.operation_id is None:
                continue

            operation.security = mapping[operation.operation_id]

    return spec


def get_default_yaml_loader() -> SchemaLoader:
    return cast(SchemaLoader, getattr(yaml, "CSafeLoader", yaml.SafeLoader))


def get_route_name(operation_id: str) -> str:
    return operation_id.replace(" ", "-")


def get_route_prefix(mixed: Url) -> str:
    return (URL(mixed) if isinstance(mixed, str) else mixed).path


def read_openapi_schema(
    path: Path, *, loader: Union[SchemaLoader, None] = None
) -> DictStrAny:
    """Read OpenAPI Schema from given path.

    By default, when ``loader`` is not explicitly passed, attempt to guess
    schema loader function from path extension.

    ``loader`` should be a callable, which receives ``bytes`` and returns
    ``Dict[str, Any]`` of OpenAPI Schema.

    By default, next schema loader used,

    - :func:`json.loads` for ``openapi.json``
    - ``yaml.load`` for ``openapi.yaml``
    """
    if loader is None:
        if path.suffix == ".json":
            loader = json.loads
        elif path.suffix in {".yml", ".yaml"}:
            loader = partial(yaml.load, Loader=get_default_yaml_loader())

    if loader is not None:
        return loader(path.read_bytes())

    raise ConfigurationError(
        f"Unsupported OpenAPI schema file: {path}. At a moment rororo "
        "supports loading OpenAPI schemas from: .json, .yml, .yaml files"
    )


@overload
def setup_openapi(
    app: web.Application,
    schema_path: Union[str, Path],
    *operations: OperationTableDef,
    server_url: Union[Url, None] = None,
    is_validate_response: bool = True,
    has_openapi_schema_handler: bool = True,
    use_error_middleware: bool = True,
    error_middleware_kwargs: Union[ErrorMiddlewareKwargsDict, None] = None,
    use_cors_middleware: bool = True,
    cors_middleware_kwargs: Union[CorsMiddlewareKwargsDict, None] = None,
    schema_loader: Union[SchemaLoader, None] = None,
    cache_create_schema_and_spec: bool = False,
    validate_email_kwargs: Union[ValidateEmailKwargsDict, None] = None,
) -> web.Application:
    ...


@overload
def setup_openapi(
    app: web.Application,
    *operations: OperationTableDef,
    schema: DictStrAny,
    spec: Spec,
    server_url: Union[Url, None] = None,
    is_validate_response: bool = True,
    has_openapi_schema_handler: bool = True,
    use_error_middleware: bool = True,
    error_middleware_kwargs: Union[ErrorMiddlewareKwargsDict, None] = None,
    use_cors_middleware: bool = True,
    cors_middleware_kwargs: Union[CorsMiddlewareKwargsDict, None] = None,
    validate_email_kwargs: Union[ValidateEmailKwargsDict, None] = None,
) -> web.Application:
    ...


def setup_openapi(  # type: ignore[misc]
    app: web.Application,
    schema_path: Union[str, Path, None] = None,
    *operations: OperationTableDef,
    schema: Union[DictStrAny, None] = None,
    spec: Union[Spec, None] = None,
    server_url: Union[Url, None] = None,
    is_validate_response: bool = True,
    has_openapi_schema_handler: bool = True,
    use_error_middleware: bool = True,
    error_middleware_kwargs: Union[ErrorMiddlewareKwargsDict, None] = None,
    use_cors_middleware: bool = True,
    cors_middleware_kwargs: Union[CorsMiddlewareKwargsDict, None] = None,
    schema_loader: Union[SchemaLoader, None] = None,
    cache_create_schema_and_spec: bool = False,
    validate_email_kwargs: Union[ValidateEmailKwargsDict, None] = None,
) -> web.Application:
    """Setup OpenAPI schema to use with aiohttp.web application.

    Unlike `aiohttp-apispec <https://aiohttp-apispec.readthedocs.io/>`_ and
    other tools, which provides OpenAPI/Swagger support for aiohttp.web
    applications, *rororo* changes the way of using OpenAPI schema with
    ``aiohttp.web`` apps.

    *rororo* using schema first approach and relies on concrete OpenAPI schema
    file, path to which need to be registered on application startup (mostly
    inside of ``create_app`` factory or right after
    :class:`aiohttp.web.Application` instantiation).

    And as valid OpenAPI schema ensure unique ``operationId`` used accross the
    schema *rororo* uses them as a key while telling aiohttp.web to use given
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

    you have 2 options of telling *rororo* how to use specific server URL.

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

    After, *rororo* will try to equal current app settings level with the
    schema and if URL matched, will use given server URL for finding out
    route prefix.

    By default, *rororo* will validate operation responses against OpenAPI
    schema. To disable this feature, pass ``is_validate_response`` falsy flag.

    By default, *rororo* will share the OpenAPI schema which is registered
    for your aiohttp.web application. In case if you don't want to share this
    schema, pass ``has_openapi_schema_handler=False`` on setting up OpenAPI.

    By default, *rororo* will enable
    :func:`aiohttp_middlewares.cors.cors_middleware` without any settings and
    :func:`aiohttp_middlewares.error.error_middleware` with custom error
    handler to ensure that security / validation errors does not provide any
    mess to stdout. Pass ``use_cors_middleware`` /
    ``use_error_middleware`` to change or entirely disable this default
    behaviour.

    For passing custom options to CORS middleware, use
    ``cors_middleware_kwargs`` mapping. If kwarg does not support by CORS
    middleware - *rororo* will raise a ``ConfigurationError``. All list of
    options available at documentation for
    :func:`aiohttp_middlewares.cors.cors_middleware`.

    To simplify things *rororo* expects on OpenAPI 3 path and do reading schema
    from file and specifying ``openapi_core.schema.specs.models.Spec`` instance
    inside of :func:`rororo.openapi.setup_openapi` call.

    However, it is possible to completely customize this default behaviour and
    pass OpenAPI ``schema`` and ``spec`` instance directly. In that case
    ``schema`` keyword argument should contains raw OpenAPI 3 schema as
    ``Dict[str, Any]``, while ``spec`` to be an
    ``openapi_core.schema.specs.models.Spec`` instance.

    This behaviour might be helpful if you'd like to cache reading schema and
    instantiating spec within tests or other environments, which requires
    multiple :func:`rororo.openapi.setup_openapi` calls.

    .. code-block:: python

        from pathlib import Path

        import yaml
        from aiohttp import web
        from openapi_core.shortcuts import create_spec
        from rororo import setup_openapi


        # Reusable OpenAPI data
        openapi_yaml = Path(__file__).parent / "openapi.yaml"
        schema = yaml.load(
            openapi_yaml.read_bytes(), Loader=yaml.CSafeLoader
        )
        spec = create_spec(schema)

        # Create OpenAPI 3 aiohttp.web server application
        app = setup_openapi(web.Application(), schema=schema, spec=spec)

    For default behaviour, with passing ``schema_path``, there are few options
    on customizing schema load process as well,

    By default, *rororo* will use :func:`json.loads` to load OpenAPI schema
    content from JSON file and ``yaml.CSafeLoader`` if it is available to load
    schema content from YAML files (with fallback to ``yaml.SafeLoader``). But,
    for performance considreations, you might use any other function to load
    the schema. Example below illustrates how to use ``ujson.loads`` function
    to load content from JSON schema,

    .. code-block:: python

        import ujson

        app = setup_openapi(
            web.Application(),
            Path(__file__).parent / "openapi.json",
            operations,
            schema_loader=ujson.loads,
        )

    Schema loader function expects ``bytes`` as only argument and should return
    ``Dict[str, Any]`` as OpenAPI schema dict.

    .. danger::
        By default *rororo* does not cache slow calls to read OpenAPI schema
        and creating its spec. But sometimes, for example in tests, it is
        sufficient to cache those calls. To enable cache behaviour pass
        ``cache_create_schema_and_spec=True`` or even better,
        ``cache_create_schema_and_spec=settings.is_test``.

        But this may result in unexpected issues, as schema and spec will be
        cached once and on next call it will result cached data instead to
        attempt read fresh schema from the disk and instantiate OpenAPI Spec
        instance.

    By default, *rororo* using ``validate_email`` function from
    `email-validator <https://github.com/JoshData/python-email-validator>`_
    library to validate email strings, which has been declared in OpenAPI
    schema as,

    .. code-block:: yaml

        components:
          schemas:
            Email:
              type: "string"
              format: "email"

    In most cases ``validate_email(email)`` call should be enough, but in case
    if you need to pass extra ``**kwargs`` for validating email strings, setup
    ``validate_email_kwargs`` such as,

    .. code-block:: python

        app = setup_openapi(
            web.Application(),
            Path(__file__).parent / "openapi.json",
            operations,
            validate_email_kwargs={"check_deliverability": False},
        )

    """

    if isinstance(schema_path, OperationTableDef):
        operations = (schema_path, *operations)
        schema_path = None

    if schema is None and spec is None:
        if schema_path is None:
            raise ConfigurationError(
                "Please supply only `spec` keyword argument, or only "
                "`schema_path` positional argument, not both."
            )

        # Ensure OpenAPI schema is a readable file
        path = (
            Path(schema_path) if isinstance(schema_path, str) else schema_path
        )
        if not path.exists() or not path.is_file():
            uid = os.getuid()
            raise ConfigurationError(
                f"Unable to find OpenAPI schema file at {path}. Please check "
                "that file exists at given path and readable by current user "
                f"ID: {uid}"
            )

        # Create the spec and put it to the application dict as well
        create_func: CreateSchemaAndSpec = (
            create_schema_and_spec_with_cache  # type: ignore[assignment]
            if cache_create_schema_and_spec
            else create_schema_and_spec
        )

        try:
            schema, spec = create_func(path, schema_loader=schema_loader)
        except Exception:
            raise ConfigurationError(
                f"Unable to load valid OpenAPI schema in {path}. In most "
                "cases it means that given file doesn't contain valid OpenAPI "
                "3 schema. To get full details about errors run "
                f"`openapi-spec-validator {path.absolute()}`"
            )
    elif schema_path is not None:
        warnings.warn(
            "You supplied `schema_path` positional argument as well as "
            "supplying `schema` & `spec` keyword arguments. `schema_path` "
            "will be ignored in favor of `schema` & `spec` args."
        )

    # Fix all operation securities within OpenAPI spec
    spec = fix_spec_operations(spec, cast(DictStrAny, schema))

    # Store schema, spec, and validate email kwargs in application dict
    app[APP_OPENAPI_SCHEMA_KEY] = schema
    app[APP_OPENAPI_SPEC_KEY] = spec
    app[APP_VALIDATE_EMAIL_KWARGS_KEY] = validate_email_kwargs

    # Register the route to dump openapi schema used for the application if
    # required
    route_prefix = find_route_prefix(
        cast(DictStrAny, schema),
        server_url=server_url,
        settings=app.get(APP_SETTINGS_KEY),
    )
    if has_openapi_schema_handler:
        app.router.add_get(
            add_prefix("/openapi.{schema_format}", route_prefix),
            views.openapi_schema,
        )

    # Register all operation handlers to web application
    for item in operations:
        app.router.add_routes(
            convert_operations_to_routes(item, spec, prefix=route_prefix)
        )

    # Add OpenAPI middleware
    kwargs = error_middleware_kwargs or {}
    kwargs.setdefault("default_handler", views.default_error_handler)

    try:
        app.middlewares.insert(
            0,
            openapi_middleware(
                is_validate_response=is_validate_response,
                use_error_middleware=use_error_middleware,
                error_middleware_kwargs=kwargs,
            ),
        )
    except TypeError:
        raise ConfigurationError(
            "Unsupported kwargs passed to error middleware. Please check "
            "given kwargs and remove unsupported ones: "
            f"{error_middleware_kwargs!r}"
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
                f"{cors_middleware_kwargs!r}"
            )

    return app
