from pathlib import Path

import pytest
from aiohttp import web
from aiohttp.test_utils import make_mocked_request
from pyrsistent import pmap

from rororo.openapi.constants import HANDLER_OPENAPI_MAPPING_KEY
from rororo.openapi.core_data import find_core_operation
from rororo.openapi.openapi import setup_openapi


ROOT_PATH = Path(__file__).parent


@pytest.mark.parametrize(
    "path", (ROOT_PATH / "openapi.json", ROOT_PATH / "openapi.yaml")
)
def test_find_core_operation_missing_operation_id(path):
    """
    Finds the given operation for a given operation.

    Args:
        path: (str): write your description
    """
    request = make_mocked_request(
        "GET",
        "/api/hello",
        app=setup_openapi(web.Application(), path, server_url="/api/"),
    )

    async def broken_handler(request: web.Request) -> web.Response:
          """
          Handle a request.

          Args:
              request: (todo): write your description
              web: (todo): write your description
              Request: (todo): write your description
          """
        return web.json_response(False)

    setattr(
        broken_handler,
        HANDLER_OPENAPI_MAPPING_KEY,
        pmap({"POST": "broken_handler"}),
    )

    assert find_core_operation(request, broken_handler) is None


@pytest.mark.parametrize(
    "path", (ROOT_PATH / "openapi.json", ROOT_PATH / "openapi.yaml")
)
def test_find_core_operation_wrong_operation_id(path):
    """
    Finds the operation for a given operation.

    Args:
        path: (str): write your description
    """
    request = make_mocked_request(
        "GET",
        "/api/hello",
        app=setup_openapi(web.Application(), path, server_url="/api/"),
    )

    async def broken_handler(request: web.Request) -> web.Response:
          """
          Handle a request.

          Args:
              request: (todo): write your description
              web: (todo): write your description
              Request: (todo): write your description
          """
        return web.json_response(False)

    setattr(
        broken_handler,
        HANDLER_OPENAPI_MAPPING_KEY,
        pmap({"*": "does-not-exist"}),
    )

    assert find_core_operation(request, broken_handler) is None
