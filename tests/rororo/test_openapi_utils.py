import pytest
from aiohttp import web
from aiohttp_middlewares import error_middleware

from rororo.openapi.utils import add_prefix, get_openapi_context


@pytest.mark.parametrize(
    "path, prefix, expected",
    (
        ("/", "", "/"),
        ("/", "/", "/"),
        ("/items", "/api", "/api/items"),
        ("/items", "/api/", "/api/items"),
    ),
)
def test_add_prefix(path, prefix, expected):
    assert add_prefix(path, prefix) == expected


async def test_get_openapi_context_error(aiohttp_client):
    async def handler(request: web.Request) -> web.Response:
        return web.json_response(get_openapi_context(request).operation.id)

    app = web.Application(middlewares=(error_middleware(),))
    app.router.add_get("/", handler)

    client = await aiohttp_client(app)
    response = await client.get("/")
    assert response.status == 500
    assert (await response.json())["detail"].split()[0] == "Request"
