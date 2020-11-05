import datetime
import io
import json
import zipfile
from pathlib import Path

import pyrsistent
import pytest
import yaml
from aiohttp import web
from openapi_core.shortcuts import create_spec
from yarl import URL

from rororo import (
    BaseSettings,
    get_openapi_context,
    get_openapi_schema,
    get_openapi_spec,
    openapi_context,
    OperationTableDef,
    setup_openapi,
    setup_settings_from_environ,
)
from rororo.annotations import DictStrAny
from rororo.openapi import get_validated_data
from rororo.openapi.exceptions import (
    ConfigurationError,
    OperationError,
    ValidationError,
)


ROOT_PATH = Path(__file__).parent

INVALID_OPENAPI_JSON_PATH = ROOT_PATH / "invalid-openapi.json"
INVALID_OPENAPI_YAML_PATH = ROOT_PATH / "invalid-openapi.yaml"
OPENAPI_JSON_PATH = ROOT_PATH / "openapi.json"
OPENAPI_YAML_PATH = ROOT_PATH / "openapi.yaml"
TEST_NESTED_OBJECT = {
    "uid": "6fccda1b-0873-4c8a-bceb-a2acfe5851da",
    "type": "nested-object",
    "data": {
        "data_item": {"key": "value1", "any_data": {}},
        "data_items": [
            {"key": "value2", "any_data": {"two": 2}},
            {"key": "value3", "any_data": {"three": 3}},
        ],
        "str_items": ["1", "2", "3"],
    },
    "any_data": {"key1": "value1", "key2": "value2", "list": [1, 2, 3]},
}

operations = OperationTableDef()
invalid_operations = OperationTableDef()


def custom_json_loader(content: bytes) -> DictStrAny:
    """
    Loads the content - serialization.

    Args:
        content: (str): write your description
    """
    return json.load(io.BytesIO(content))


def custom_yaml_loader(content: bytes) -> DictStrAny:
    """
    Custom yaml file.

    Args:
        content: (str): write your description
    """
    return yaml.load(content, Loader=yaml.SafeLoader)


@invalid_operations.register("does-not-exist")
async def does_not_exist(request: web.Request) -> web.Response:
      """
      Return true if the user exist.

      Args:
          request: (todo): write your description
          web: (todo): write your description
          Request: (todo): write your description
      """
    return web.Response(text="Hello, world!")


@operations.register("create-post")
async def create_post(request: web.Request) -> web.Response:
      """
      Create a post request.

      Args:
          request: (todo): write your description
          web: (todo): write your description
          Request: (todo): write your description
      """
    data = get_validated_data(request)

    published_at: datetime.datetime = data["published_at"]
    if published_at.tzinfo is None:
        raise ValidationError.from_dict(body={"published_at": "Invalid value"})

    return web.json_response(
        {**data, "id": 1, "published_at": data["published_at"].isoformat()},
        status=201,
    )


@operations.register
async def hello_world(request: web.Request) -> web.Response:
      """
      Displays the world.

      Args:
          request: (todo): write your description
          web: (todo): write your description
          Request: (todo): write your description
      """
    with openapi_context(request) as context:
        name = context.parameters.query.get("name") or "world"
        email = context.parameters.query.get("email") or "world@example.com"
        return web.json_response(
            {"message": f"Hello, {name}!", "email": email}
        )


@operations.register
async def retrieve_any_object_from_request_body(
    request: web.Request,
) -> web.Response:
      """
      Retrieves a request from the given request.

      Args:
          request: (todo): write your description
          web: (todo): write your description
          Request: (todo): write your description
      """
    return web.json_response(pyrsistent.thaw(get_validated_data(request)))


@operations.register
async def retrieve_array_from_request_body(
    request: web.Request,
) -> web.Response:
      """
      Retrieve a single array of the given request.

      Args:
          request: (todo): write your description
          web: (todo): write your description
          Request: (todo): write your description
      """
    with openapi_context(request) as context:
        return web.json_response(pyrsistent.thaw(context.data))


@operations.register
async def retrieve_empty(request: web.Request) -> web.Response:
      """
      Retrieve the empty empty string.

      Args:
          request: (todo): write your description
          web: (todo): write your description
          Request: (todo): write your description
      """
    context = get_openapi_context(request)
    return web.Response(
        status=204, headers={"X-API-Key": context.security.get("apiKey") or ""}
    )


@operations.register
async def retrieve_invalid_response(request: web.Request) -> web.Response:
      """
      Retrieves a json response for a request.

      Args:
          request: (todo): write your description
          web: (todo): write your description
          Request: (todo): write your description
      """
    return web.json_response({})


@operations.register
async def retrieve_post(request: web.Request) -> web.Response:
      """
      Retrieve the post request.

      Args:
          request: (todo): write your description
          web: (todo): write your description
          Request: (todo): write your description
      """
    context = get_openapi_context(request)
    return web.json_response(
        {"id": context.parameters.path["post_id"], "title": "The Post"}
    )


@operations.register
async def retrieve_nested_object_from_request_body(
    request: web.Request,
) -> web.Response:
      """
      Retrieve a json object from a json object.

      Args:
          request: (todo): write your description
          web: (todo): write your description
          Request: (todo): write your description
      """
    with openapi_context(request) as context:
        data = pyrsistent.thaw(context.data)
        data["uid"] = str(data["uid"])

        return web.json_response(
            data,
            headers={
                "X-Data-Type": str(type(context.data)),
                "X-Data-Data-Data-Items-Type": str(
                    type(context.data["data"]["data_items"])
                ),
                "X-Data-Data-Str-Items-Type": str(
                    type(context.data["data"]["str_items"])
                ),
                "X-Data-UID-Type": str(type(context.data["uid"])),
            },
        )


@operations.register
async def retrieve_zip(request: web.Request) -> web.Response:
      """
      Retrieve a zip file

      Args:
          request: (todo): write your description
          web: (todo): write your description
          Request: (todo): write your description
      """
    output = io.BytesIO()

    with zipfile.ZipFile(output, "w") as handler:
        handler.writestr("hello.txt", "Hello, world!")

    output.seek(0)
    return web.Response(
        body=output,
        content_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=hello.zip"},
    )


@operations.register
async def upload_image(request: web.Request) -> web.Response:
      """
      Uploads an image.

      Args:
          request: (todo): write your description
          web: (todo): write your description
          Request: (todo): write your description
      """
    return web.Response(
        body=get_openapi_context(request).data,
        content_type=request.content_type,
        status=201,
    )


@operations.register
async def upload_text(request: web.Request) -> web.Response:
      """
      Upload text to webapi.

      Args:
          request: (todo): write your description
          web: (todo): write your description
          Request: (todo): write your description
      """
    return web.Response(
        text=get_openapi_context(request).data,
        content_type=request.content_type,
        status=201,
    )


@pytest.mark.parametrize("schema_path", (OPENAPI_JSON_PATH, OPENAPI_YAML_PATH))
async def test_any_object_request_body(aiohttp_client, schema_path):
      """
      Sends an object in aio.

      Args:
          aiohttp_client: (todo): write your description
          schema_path: (str): write your description
      """
    app = setup_openapi(
        web.Application(), schema_path, operations, server_url=URL("/api/")
    )

    client = await aiohttp_client(app)
    response = await client.post("/api/any-object", json=TEST_NESTED_OBJECT)
    assert response.status == 200
    assert await response.json() == TEST_NESTED_OBJECT


@pytest.mark.parametrize(
    "data, expected_status, expected_response",
    (
        (
            {},
            422,
            {"detail": [{"loc": ["body"], "message": "[] is too short"}]},
        ),
        (
            [],
            422,
            {"detail": [{"loc": ["body"], "message": "[] is too short"}]},
        ),
        (
            [""],
            422,
            {"detail": [{"loc": ["body", 0], "message": "'' is too short"}]},
        ),
        (["Hello", "world!"], 200, ["Hello", "world!"]),
    ),
)
async def test_array_request_body(
    aiohttp_client, data, expected_status, expected_response
):
      """
      Sends an array of arrays.

      Args:
          aiohttp_client: (todo): write your description
          data: (array): write your description
          expected_status: (str): write your description
          expected_response: (str): write your description
      """
    app = setup_openapi(
        web.Application(),
        OPENAPI_YAML_PATH,
        operations,
        server_url=URL("/api"),
    )

    client = await aiohttp_client(app)
    response = await client.post("/api/array", json=data)
    assert response.status == expected_status
    assert await response.json() == expected_response


@pytest.mark.parametrize("schema_path", (OPENAPI_JSON_PATH, OPENAPI_YAML_PATH))
async def test_create_post_201(aiohttp_client, schema_path):
      """
      Create a new post request.

      Args:
          aiohttp_client: (todo): write your description
          schema_path: (str): write your description
      """
    app = setup_openapi(
        web.Application(), schema_path, operations, server_url="/api/"
    )
    published_at = "2020-04-01T12:00:00+02:00"

    client = await aiohttp_client(app)
    response = await client.post(
        "/api/create-post",
        json={
            "title": "Post",
            "slug": "post",
            "content": "Post Content",
            "published_at": published_at,
        },
    )
    assert response.status == 201
    assert await response.json() == {
        "id": 1,
        "title": "Post",
        "slug": "post",
        "content": "Post Content",
        "published_at": published_at,
    }


@pytest.mark.parametrize(
    "schema_path, invalid_data, expected_detail",
    (
        (
            OPENAPI_JSON_PATH,
            {},
            [
                {"loc": ["body", "title"], "message": "Field required"},
                {"loc": ["body", "slug"], "message": "Field required"},
                {"loc": ["body", "content"], "message": "Field required"},
                {"loc": ["body", "published_at"], "message": "Field required"},
            ],
        ),
        (
            OPENAPI_YAML_PATH,
            {"title": "Title"},
            [
                {"loc": ["body", "slug"], "message": "Field required"},
                {"loc": ["body", "content"], "message": "Field required"},
                {"loc": ["body", "published_at"], "message": "Field required"},
            ],
        ),
        (
            OPENAPI_JSON_PATH,
            {"title": "Title", "slug": "slug"},
            [
                {"loc": ["body", "content"], "message": "Field required"},
                {"loc": ["body", "published_at"], "message": "Field required"},
            ],
        ),
        (
            OPENAPI_YAML_PATH,
            {"title": "Title", "slug": "slug", "content": "Content"},
            [{"loc": ["body", "published_at"], "message": "Field required"}],
        ),
    ),
)
async def test_create_post_422(
    aiohttp_client, schema_path, invalid_data, expected_detail
):
      """
      Create a new post on the server.

      Args:
          aiohttp_client: (todo): write your description
          schema_path: (str): write your description
          invalid_data: (str): write your description
          expected_detail: (todo): write your description
      """
    app = setup_openapi(
        web.Application(),
        schema_path,
        operations,
        server_url=URL("/dev-api"),
    )

    client = await aiohttp_client(app)
    response = await client.post("/dev-api/create-post", json=invalid_data)
    assert response.status == 422
    assert (await response.json())["detail"] == expected_detail


@pytest.mark.parametrize(
    "schema_path, schema_loader",
    (
        (OPENAPI_JSON_PATH, custom_json_loader),
        (OPENAPI_YAML_PATH, custom_yaml_loader),
    ),
)
def test_custom_schema_loader(schema_path, schema_loader):
    """
    Creates a schema loader.

    Args:
        schema_path: (str): write your description
        schema_loader: (todo): write your description
    """
    app = setup_openapi(
        web.Application(),
        schema_path,
        operations,
        server_url="/api/",
        schema_loader=schema_loader,
    )
    assert isinstance(get_openapi_schema(app), dict)


@pytest.mark.parametrize("schema_path", (OPENAPI_JSON_PATH, OPENAPI_YAML_PATH))
async def test_email_format(aiohttp_client, schema_path):
      """
      Format an email format.

      Args:
          aiohttp_client: (todo): write your description
          schema_path: (str): write your description
      """
    app = setup_openapi(
        web.Application(), schema_path, operations, server_url="/api/"
    )

    client = await aiohttp_client(app)
    response = await client.get(
        "/api/hello", params={"email": "email@example.com"}
    )
    assert response.status == 200
    assert (await response.json())["email"] == "email@example.com"


@pytest.mark.parametrize("schema_path", (OPENAPI_JSON_PATH, OPENAPI_YAML_PATH))
async def test_invalid_parameter_format(aiohttp_client, schema_path):
      """
      Validate the api endpoint.

      Args:
          aiohttp_client: (todo): write your description
          schema_path: (str): write your description
      """
    app = setup_openapi(
        web.Application(), schema_path, operations, server_url="/api/"
    )

    client = await aiohttp_client(app)
    response = await client.get("/api/posts/not-an-integer")
    assert response.status == 422
    assert await response.json() == {
        "detail": [
            {
                "loc": ["parameters", "post_id"],
                "message": "'not-an-integer' is not a type of 'integer'",
            }
        ]
    }


@pytest.mark.parametrize("schema_path", (OPENAPI_JSON_PATH, OPENAPI_YAML_PATH))
async def test_invalid_parameter_value(aiohttp_client, schema_path):
      """
      Requests the value of a webhook.

      Args:
          aiohttp_client: (todo): write your description
          schema_path: (str): write your description
      """
    app = setup_openapi(
        web.Application(), schema_path, operations, server_url="/api/"
    )

    client = await aiohttp_client(app)
    response = await client.get("/api/posts/0")
    assert response.status == 422
    assert await response.json() == {
        "detail": [
            {
                "loc": ["parameters", "post_id"],
                "message": "0 is less than the minimum of 1",
            }
        ]
    }


def test_get_openapi_schema_no_schema():
    """
    Retrieve the openapi file.

    Args:
    """
    with pytest.raises(ConfigurationError):
        get_openapi_schema(web.Application())


def test_get_openapi_spec_no_spec():
    """
    Get the openapi specification

    Args:
    """
    with pytest.raises(ConfigurationError):
        get_openapi_spec(web.Application())


@pytest.mark.parametrize("schema_path", (OPENAPI_JSON_PATH, OPENAPI_YAML_PATH))
async def test_multiple_request_errors(aiohttp_client, schema_path):
      """
      Test for valid http errors.

      Args:
          aiohttp_client: (todo): write your description
          schema_path: (str): write your description
      """
    app = setup_openapi(
        web.Application(), schema_path, operations, server_url="/api/"
    )

    client = await aiohttp_client(app)
    response = await client.get("/api/hello?name=&email=")
    assert response.status == 422
    assert await response.json() == {
        "detail": [
            {
                "loc": ["parameters", "name"],
                "message": "Empty parameter value",
            },
            {
                "loc": ["parameters", "email"],
                "message": "Empty parameter value",
            },
        ]
    }


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
      """
      Perform an openapi.

      Args:
          aiohttp_client: (todo): write your description
          schema_path: (str): write your description
          query_string: (str): write your description
          expected_message: (str): write your description
      """
    app = setup_openapi(
        web.Application(), schema_path, operations, server_url="/api"
    )

    client = await aiohttp_client(app)
    url = "/api/hello"

    response = await client.get(
        f"{url}{query_string}" if query_string is not None else url
    )
    assert response.status == 200
    assert (await response.json())["message"] == expected_message


@pytest.mark.parametrize("is_enabled", (False, True))
async def test_openapi_validate_response(aiohttp_client, is_enabled):
      """
      Test if the openapi server.

      Args:
          aiohttp_client: (todo): write your description
          is_enabled: (bool): write your description
      """
    app = web.Application()
    setup_openapi(
        app,
        OPENAPI_YAML_PATH,
        operations,
        server_url="/api",
        is_validate_response=is_enabled,
    )

    client = await aiohttp_client(app)
    response = await client.get("/api/hello")
    assert response.status == 200
    assert await response.json() == {
        "message": "Hello, world!",
        "email": "world@example.com",
    }


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
      """
      Test for openapi schema handler.

      Args:
          aiohttp_client: (todo): write your description
          has_openapi_schema_handler: (todo): write your description
          url: (str): write your description
          expected_status: (str): write your description
      """
    app = web.Application()
    setup_openapi(
        app,
        OPENAPI_YAML_PATH,
        operations,
        server_url=URL("/api"),
        has_openapi_schema_handler=has_openapi_schema_handler,
    )

    client = await aiohttp_client(app)
    response = await client.get(url)
    assert response.status == expected_status


@pytest.mark.parametrize(
    "schema_path, headers, expected",
    (
        (OPENAPI_JSON_PATH, {}, ""),
        (OPENAPI_JSON_PATH, {"X-API-Key": "apiKey"}, "apiKey"),
        (OPENAPI_YAML_PATH, {}, ""),
        (OPENAPI_YAML_PATH, {"X-API-Key": "apiKey"}, "apiKey"),
    ),
)
async def test_optional_security_scheme(
    aiohttp_client, schema_path, headers, expected
):
      """
      Test if security security security security optional optional.

      Args:
          aiohttp_client: (todo): write your description
          schema_path: (str): write your description
          headers: (str): write your description
          expected: (str): write your description
      """
    app = setup_openapi(
        web.Application(), schema_path, operations, server_url="/api/"
    )

    client = await aiohttp_client(app)
    response = await client.get("/api/empty", headers=headers)
    assert response.status == 204
    assert response.headers["X-API-Key"] == expected


@pytest.mark.parametrize("schema_path", (OPENAPI_JSON_PATH, OPENAPI_YAML_PATH))
async def test_request_body_nested_object(aiohttp_client, schema_path):
      """
      Test for aiohttp request object.

      Args:
          aiohttp_client: (todo): write your description
          schema_path: (str): write your description
      """
    app = setup_openapi(
        web.Application(), schema_path, operations, server_url="/api/"
    )

    client = await aiohttp_client(app)
    response = await client.post("/api/nested-object", json=TEST_NESTED_OBJECT)
    assert response.status == 200
    assert response.headers["X-Data-Type"] == "<class 'pyrsistent._pmap.PMap'>"
    assert (
        response.headers["X-Data-Data-Data-Items-Type"]
        == "<class 'pvectorc.PVector'>"
    )
    assert (
        response.headers["X-Data-Data-Str-Items-Type"]
        == "<class 'pvectorc.PVector'>"
    )
    assert response.headers["X-Data-UID-Type"] == "<class 'uuid.UUID'>"
    assert await response.json() == TEST_NESTED_OBJECT


@pytest.mark.parametrize(
    "schema_path, loader",
    (
        (OPENAPI_JSON_PATH, custom_json_loader),
        (OPENAPI_YAML_PATH, custom_yaml_loader),
    ),
)
async def test_setup_openapi_schema_and_spec(
    aiohttp_client, schema_path, loader
):
      """
      Test for openiohttp specification.

      Args:
          aiohttp_client: (todo): write your description
          schema_path: (str): write your description
          loader: (todo): write your description
      """
    schema = loader(schema_path.read_bytes())
    spec = create_spec(schema)

    app = setup_openapi(
        web.Application(),
        operations,
        schema=schema,
        spec=spec,
        server_url="/api/",
    )

    client = await aiohttp_client(app)
    response = await client.get("/api/hello")
    assert response.status == 200
    assert await response.json() == {
        "message": "Hello, world!",
        "email": "world@example.com",
    }


@pytest.mark.parametrize(
    "schema_path, loader",
    (
        (OPENAPI_JSON_PATH, custom_json_loader),
        (OPENAPI_YAML_PATH, custom_yaml_loader),
    ),
)
async def test_setup_openapi_schema_and_path_ignore_invalid_schema_path(
    aiohttp_client, schema_path, loader
):
      """
      Test for openiohttp specification.

      Args:
          aiohttp_client: (todo): write your description
          schema_path: (todo): write your description
          loader: (todo): write your description
      """
    schema = loader(schema_path.read_bytes())
    spec = create_spec(schema)

    setup_openapi(
        web.Application(),
        INVALID_OPENAPI_JSON_PATH,
        operations,
        schema=schema,
        spec=spec,
        server_url="/api/",
    )


@pytest.mark.parametrize("schema_path", (OPENAPI_JSON_PATH, OPENAPI_YAML_PATH))
def test_setup_openapi_invalid_operation(schema_path):
    """
    Test if the schema is valid.

    Args:
        schema_path: (str): write your description
    """
    with pytest.raises(OperationError):
        setup_openapi(
            web.Application(),
            schema_path,
            invalid_operations,
            server_url="/api",
        )


def test_setup_openapi_invalid_path():
    """
    Test if the testapi setup. pytest

    Args:
    """
    with pytest.raises(ConfigurationError):
        setup_openapi(
            web.Application(), ROOT_PATH / "does-not-exist.yaml", operations
        )


def test_setup_openapi_invalid_file():
    """
    Setup the testapi setup.

    Args:
    """
    with pytest.raises(ConfigurationError):
        setup_openapi(web.Application(), ROOT_PATH / "settings.py", operations)


@pytest.mark.parametrize(
    "schema_path", (INVALID_OPENAPI_JSON_PATH, INVALID_OPENAPI_YAML_PATH)
)
def test_setup_openapi_invalid_spec(schema_path):
    """
    Validate the specification of a schema against a schema.

    Args:
        schema_path: (str): write your description
    """
    with pytest.raises(ConfigurationError):
        setup_openapi(web.Application(), schema_path, operations)


@pytest.mark.parametrize(
    "schema_path, level, url, expected_status",
    (
        (OPENAPI_JSON_PATH, "test", "/api/hello", 200),
        (OPENAPI_JSON_PATH, "test", "/dev-api/hello", 404),
        (OPENAPI_YAML_PATH, "test", "/api/hello", 200),
        (OPENAPI_YAML_PATH, "test", "/dev-api/hello", 404),
        (OPENAPI_JSON_PATH, "dev", "/api/hello", 404),
        (OPENAPI_JSON_PATH, "dev", "/dev-api/hello", 200),
        (OPENAPI_YAML_PATH, "dev", "/api/hello", 404),
        (OPENAPI_YAML_PATH, "dev", "/dev-api/hello", 200),
    ),
)
async def test_setup_openapi_server_url_from_settings(
    monkeypatch, aiohttp_client, schema_path, level, url, expected_status
):
      """
      Make a url for a patch.

      Args:
          monkeypatch: (todo): write your description
          aiohttp_client: (todo): write your description
          schema_path: (str): write your description
          level: (str): write your description
          url: (str): write your description
          expected_status: (str): write your description
      """
    monkeypatch.setenv("LEVEL", level)

    app = setup_openapi(
        setup_settings_from_environ(web.Application(), BaseSettings),
        schema_path,
        operations,
    )

    client = await aiohttp_client(app)
    response = await client.get(url)
    assert response.status == expected_status


@pytest.mark.parametrize("schema_path", (OPENAPI_JSON_PATH, OPENAPI_YAML_PATH))
def test_setup_openapi_server_url_invalid_level(monkeypatch, schema_path):
    """
    Setup the openapi environment.

    Args:
        monkeypatch: (todo): write your description
        schema_path: (str): write your description
    """
    monkeypatch.setenv("LEVEL", "prod")

    with pytest.raises(ConfigurationError):
        setup_openapi(
            setup_settings_from_environ(web.Application(), BaseSettings),
            schema_path,
            operations,
        )


@pytest.mark.parametrize("schema_path", (OPENAPI_JSON_PATH, OPENAPI_YAML_PATH))
def test_setup_openapi_server_url_does_not_set(schema_path):
    """
    Sets the openapi server url.

    Args:
        schema_path: (str): write your description
    """
    with pytest.raises(ConfigurationError):
        setup_openapi(web.Application(), schema_path, operations)


@pytest.mark.parametrize("schema_path", (OPENAPI_JSON_PATH, OPENAPI_YAML_PATH))
async def test_upload_image(aiohttp_client, schema_path):
      """
      Upload image for image.

      Args:
          aiohttp_client: (todo): write your description
          schema_path: (str): write your description
      """
    blank_png = (Path(__file__).parent / "data" / "blank.png").read_bytes()

    app = setup_openapi(
        web.Application(), schema_path, operations, server_url="/api"
    )

    client = await aiohttp_client(app)
    response = await client.post(
        "/api/upload-image",
        data=blank_png,
        headers={"Content-Type": "image/png"},
    )
    assert response.status == 201
    assert await response.read() == blank_png


@pytest.mark.parametrize("schema_path", (OPENAPI_JSON_PATH, OPENAPI_YAML_PATH))
async def test_upload_text(aiohttp_client, schema_path):
      """
      Test for upload text to aio.

      Args:
          aiohttp_client: (todo): write your description
          schema_path: (str): write your description
      """
    text = "Hello, world! And other things..."

    app = setup_openapi(
        web.Application(), schema_path, operations, server_url="/api"
    )

    client = await aiohttp_client(app)
    response = await client.post(
        "/api/upload-text",
        data=text.encode("utf-8"),
        headers={"Content-Type": "text/plain"},
    )
    assert response.status == 201
    assert await response.text() == text


@pytest.mark.parametrize("schema_path", (OPENAPI_JSON_PATH, OPENAPI_YAML_PATH))
async def test_validate_binary_response(aiohttp_client, schema_path):
      """
      Perform binary response.

      Args:
          aiohttp_client: (todo): write your description
          schema_path: (str): write your description
      """
    app = setup_openapi(
        web.Application(),
        schema_path,
        operations,
        server_url="/api",
        is_validate_response=True,
    )

    client = await aiohttp_client(app)
    response = await client.get("/api/download.zip")
    assert response.status == 200
    assert response.content_type == "application/zip"

    content = io.BytesIO(await response.read())
    with zipfile.ZipFile(content) as handler:
        with handler.open("hello.txt") as item:
            assert item.read() == b"Hello, world!"


@pytest.mark.parametrize("schema_path", (OPENAPI_JSON_PATH, OPENAPI_YAML_PATH))
async def test_validate_empty_response(aiohttp_client, schema_path):
      """
      Validate the condition response contains aiohttp response.

      Args:
          aiohttp_client: (todo): write your description
          schema_path: (str): write your description
      """
    app = setup_openapi(
        web.Application(),
        schema_path,
        operations,
        server_url="/api",
        is_validate_response=True,
    )

    client = await aiohttp_client(app)
    response = await client.get("/api/empty")
    assert response.status == 204


@pytest.mark.parametrize(
    "schema_path, is_validate_response, expected_status",
    (
        (OPENAPI_JSON_PATH, False, 200),
        (OPENAPI_JSON_PATH, True, 422),
        (OPENAPI_YAML_PATH, False, 200),
        (OPENAPI_JSON_PATH, True, 422),
    ),
)
async def test_validate_response(
    aiohttp_client, schema_path, is_validate_response, expected_status
):
      """
      Perform aio.

      Args:
          aiohttp_client: (todo): write your description
          schema_path: (str): write your description
          is_validate_response: (bool): write your description
          expected_status: (todo): write your description
      """
    app = setup_openapi(
        web.Application(),
        schema_path,
        operations,
        server_url="/api",
        is_validate_response=is_validate_response,
    )

    client = await aiohttp_client(app)
    response = await client.get("/api/invalid-response")
    assert response.status == expected_status


@pytest.mark.parametrize("schema_path", (OPENAPI_JSON_PATH, OPENAPI_YAML_PATH))
async def test_validate_response_error(aiohttp_client, schema_path):
      """
      Validate the response for an api server.

      Args:
          aiohttp_client: (todo): write your description
          schema_path: (str): write your description
      """
    app = setup_openapi(
        web.Application(),
        schema_path,
        operations,
        server_url="/api",
        is_validate_response=True,
    )

    client = await aiohttp_client(app)
    response = await client.get("/api/invalid-response")
    assert response.status == 422
    assert await response.json() == {
        "detail": [
            {"loc": ["response", "uid"], "message": "Field required"},
            {"loc": ["response", "type"], "message": "Field required"},
            {"loc": ["response", "data"], "message": "Field required"},
            {"loc": ["response", "any_data"], "message": "Field required"},
        ]
    }
