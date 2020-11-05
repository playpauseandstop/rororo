from pathlib import Path

import pytest
from aiohttp import web
from aiohttp_middlewares import cors_middleware, error_context
from yarl import URL

from rororo import OperationTableDef, setup_openapi
from rororo.openapi.exceptions import ConfigurationError


rel = Path(__file__).absolute().parent
OPENAPI_JSON_PATH = rel / "openapi.json"
OPENAPI_YAML_PATH = rel / "openapi.yaml"

operations = OperationTableDef()


@operations.register
async def hello_world(request: web.Request) -> web.Response:
      """
      This is a http request.

      Args:
          request: (todo): write your description
          web: (todo): write your description
          Request: (todo): write your description
      """
    return web.json_response("Hello, world!")


async def plain_error_handler(request: web.Request) -> web.Response:
      """
      Convert the error.

      Args:
          request: (todo): write your description
          web: (todo): write your description
          Request: (todo): write your description
      """
    with error_context(request) as context:
        return web.Response(text=context.message, status=context.status)


def has_middleware(app, middleware):
    """
    Returns true if the middleware has already been registered.

    Args:
        app: (todo): write your description
        middleware: (str): write your description
    """
    for item in app.middlewares:
        if item.__module__ == middleware.__module__:
            return True
    return False


@pytest.mark.parametrize("schema_path", (OPENAPI_JSON_PATH, OPENAPI_YAML_PATH))
async def test_custom_default_error_handler(aiohttp_client, schema_path):
      """
      Test the default error handler

      Args:
          aiohttp_client: (todo): write your description
          schema_path: (str): write your description
      """
    app = setup_openapi(
        web.Application(),
        schema_path,
        operations,
        server_url="/api/",
        error_middleware_kwargs={"default_handler": plain_error_handler},
    )
    client = await aiohttp_client(app)

    response = await client.get("/does-not-exist")
    assert response.status == 404
    assert response.content_type == "text/plain"
    assert await response.text() == "Not Found"


@pytest.mark.parametrize("schema_path", (OPENAPI_JSON_PATH, OPENAPI_YAML_PATH))
async def test_default_error_handler(aiohttp_client, schema_path):
      """
      Default handler for http error handler.

      Args:
          aiohttp_client: (todo): write your description
          schema_path: (str): write your description
      """
    app = setup_openapi(
        web.Application(),
        schema_path,
        operations,
        server_url="/api/",
    )
    client = await aiohttp_client(app)

    response = await client.get("/does-not-exist")
    assert response.status == 404
    assert await response.json() == {"detail": "Not Found"}


@pytest.mark.parametrize(
    "schema_path, is_enabled, kwargs",
    (
        (OPENAPI_JSON_PATH, False, None),
        (OPENAPI_YAML_PATH, False, None),
        (OPENAPI_JSON_PATH, True, {"allow_all": True}),
        (OPENAPI_YAML_PATH, True, {"origins": (URL("http://localhost:8000"))}),
    ),
)
def test_use_cors_middleware(schema_path, is_enabled, kwargs):
    """
    Test for middleware middleware.

    Args:
        schema_path: (str): write your description
        is_enabled: (bool): write your description
    """
    app = setup_openapi(
        web.Application(),
        schema_path,
        operations,
        server_url="/api/",
        use_cors_middleware=is_enabled,
        cors_middleware_kwargs=kwargs,
    )
    assert has_middleware(app, cors_middleware) is is_enabled


@pytest.mark.parametrize(
    "schema_path, is_enabled, expected_content_type",
    (
        (OPENAPI_JSON_PATH, False, "text/plain"),
        (OPENAPI_YAML_PATH, False, "text/plain"),
        (OPENAPI_JSON_PATH, True, "application/json"),
        (OPENAPI_YAML_PATH, True, "application/json"),
    ),
)
async def test_use_error_middleware(
    aiohttp_client, schema_path, is_enabled, expected_content_type
):
      """
      Perform middleware middleware.

      Args:
          aiohttp_client: (todo): write your description
          schema_path: (str): write your description
          is_enabled: (bool): write your description
          expected_content_type: (str): write your description
      """
    app = setup_openapi(
        web.Application(),
        schema_path,
        operations,
        server_url="/api/",
        use_error_middleware=is_enabled,
    )
    client = await aiohttp_client(app)
    response = await client.get("/does-not-exist")
    assert response.status == 404
    assert response.content_type == expected_content_type


@pytest.mark.parametrize("schema_path", (OPENAPI_JSON_PATH, OPENAPI_YAML_PATH))
def test_use_invalid_cors_middleware_kwargs(schema_path):
    """
    Validate middleware middleware that the middleware to the middleware.

    Args:
        schema_path: (str): write your description
    """
    with pytest.raises(ConfigurationError):
        setup_openapi(
            web.Application(),
            schema_path,
            operations,
            server_url="/api/",
            use_cors_middleware=True,
            cors_middleware_kwargs={"does_not_exist": True},
        )


@pytest.mark.parametrize("schema_path", (OPENAPI_JSON_PATH, OPENAPI_YAML_PATH))
def test_use_invalid_error_middleware_kwargs(schema_path):
    """
    Validate the middleware. middleware the middleware.

    Args:
        schema_path: (str): write your description
    """
    with pytest.raises(ConfigurationError):
        setup_openapi(
            web.Application(),
            schema_path,
            operations,
            server_url="/api/",
            use_error_middleware=True,
            error_middleware_kwargs={"does_not_exist": True},
        )
