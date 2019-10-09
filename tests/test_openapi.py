from pathlib import Path

import pytest
from aiohttp import web

from rororo import (
    get_openapi_schema,
    get_openapi_spec,
    openapi_context,
    OperationTableDef,
    setup_openapi,
)
from rororo.openapi.exceptions import ConfigurationError, OperationError


ROOT_PATH = Path(__file__).parent

INVALID_OPENAPI_JSON_PATH = ROOT_PATH / "invalid-openapi.json"
INVALID_OPENAPI_YAML_PATH = ROOT_PATH / "invalid-openapi.yaml"
OPENAPI_JSON_PATH = ROOT_PATH / "openapi.json"
OPENAPI_YAML_PATH = ROOT_PATH / "openapi.yaml"

operations = OperationTableDef()
invalid_operations = OperationTableDef()


@invalid_operations.register("does-not-exist")
async def does_not_exist(request: web.Request) -> web.Response:
    return web.Response(text="Hello, world!")


@operations.register
async def hello_world(request: web.Request) -> web.Response:
    with openapi_context(request) as context:
        name = context.parameters.query.get("name") or "world"
        return web.json_response({"message": f"Hello, {name}!"})


@operations.register
async def retrieve_array_from_request_body(
    request: web.Request
) -> web.Response:
    with openapi_context(request) as context:
        return web.json_response(context.data)


@pytest.mark.parametrize(
    "data, expected_status",
    (({}, 500), ([], 500), ([""], 500), (["Hello"], 200)),
)
async def test_array_request_body(aiohttp_client, data, expected_status):
    app = web.Application()
    setup_openapi(app, OPENAPI_YAML_PATH, operations, route_prefix="/api")

    client = await aiohttp_client(app)
    response = await client.post("/api/array", json=data)
    assert response.status == expected_status

    if expected_status == 200:
        assert await response.json() == data


def test_get_openapi_schema_no_schema():
    with pytest.raises(ConfigurationError):
        get_openapi_schema(web.Application())


def test_get_openapi_spec_no_spec():
    with pytest.raises(ConfigurationError):
        get_openapi_spec(web.Application())


@pytest.mark.parametrize(
    "schema_path, query_string, expected_message",
    (
        (OPENAPI_JSON_PATH, None, "Hello, world!"),
        (OPENAPI_JSON_PATH, "?name=Name", "Hello, Name!"),
        (str(OPENAPI_JSON_PATH), None, "Hello, world!"),
        (str(OPENAPI_JSON_PATH), "?name=Name", "Hello, Name!"),
        (OPENAPI_YAML_PATH, None, "Hello, world!"),
        (OPENAPI_YAML_PATH, "?name=Name", "Hello, Name!"),
        (str(OPENAPI_YAML_PATH), None, "Hello, world!"),
        (str(OPENAPI_YAML_PATH), "?name=Name", "Hello, Name!"),
    ),
)
async def test_openapi(
    aiohttp_client, schema_path, query_string, expected_message
):
    app = web.Application()
    setup_openapi(app, schema_path, operations, route_prefix="/api")

    client = await aiohttp_client(app)
    url = "/api/hello"

    response = await client.get(
        f"{url}{query_string}" if query_string is not None else url
    )
    assert response.status == 200
    assert (await response.json())["message"] == expected_message


@pytest.mark.parametrize(
    "has_openapi_schema_handler, url, expected_status",
    (
        (True, "/api/openapi.json", 200),
        (False, "/api/openapi.yaml", 404),
        (True, "/api/openapi.yaml", 200),
        (False, "/api/openapi.yaml", 404),
        (True, "/api/openapi.txt", 500),
        (False, "/api/openapi.txt", 404),
    ),
)
async def test_openapi_schema_handler(
    aiohttp_client, has_openapi_schema_handler, url, expected_status
):
    app = web.Application()
    setup_openapi(
        app,
        OPENAPI_YAML_PATH,
        operations,
        route_prefix="/api",
        has_openapi_schema_handler=has_openapi_schema_handler,
    )

    client = await aiohttp_client(app)
    response = await client.get(url)
    assert response.status == expected_status


def test_setup_openapi_invalid_operation():
    with pytest.raises(OperationError):
        setup_openapi(web.Application(), OPENAPI_YAML_PATH, invalid_operations)


def test_setup_openapi_invalid_path():
    with pytest.raises(ConfigurationError):
        setup_openapi(
            web.Application(), ROOT_PATH / "does-not-exist.yaml", operations
        )


def test_setup_openapi_invalid_file():
    with pytest.raises(ConfigurationError):
        setup_openapi(web.Application(), ROOT_PATH / "settings.py", operations)


@pytest.mark.parametrize(
    "schema_path", (INVALID_OPENAPI_JSON_PATH, INVALID_OPENAPI_YAML_PATH)
)
def test_setup_openapi_invalid_spec(schema_path):
    with pytest.raises(ConfigurationError):
        setup_openapi(web.Application(), schema_path, operations)
