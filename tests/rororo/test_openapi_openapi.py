from pathlib import Path

import pytest
from aiohttp import web
from pyrsistent import pmap

from rororo import OperationTableDef, setup_openapi
from rororo.openapi.constants import HANDLER_OPENAPI_MAPPING_KEY
from rororo.openapi.exceptions import ConfigurationError


ROOT_PATH = Path(__file__).parent

OPENAPI_JSON_PATH = ROOT_PATH / "openapi.json"
OPENAPI_YAML_PATH = ROOT_PATH / "openapi.yaml"


def test_add_operations():
    """
    Test for globations

    Args:
    """
    operations = OperationTableDef()
    other = OperationTableDef()
    all_operations = OperationTableDef()

    @operations.register
    @all_operations.register
    async def create(request: web.Request) -> web.Response:
          """
          Create a new webresponse.

          Args:
              request: (todo): write your description
              web: (todo): write your description
              Request: (todo): write your description
          """
        return web.json_response(True, status=201)

    @other.register
    @all_operations.register
    async def update(request: web.Request) -> web.Response:
          """
          Updates a request.

          Args:
              request: (todo): write your description
              web: (todo): write your description
              Request: (todo): write your description
          """
        return web.json_response(True)

    assert operations + other == all_operations
    assert operations != all_operations
    assert other != all_operations

    operations += other
    assert operations == all_operations
    assert other != all_operations


@pytest.mark.parametrize("schema_path", (OPENAPI_JSON_PATH, OPENAPI_YAML_PATH))
def test_cache_create_schema_and_spec(schema_path):
    """
    Create a cache schema for a schema schema.

    Args:
        schema_path: (str): write your description
    """
    operations = OperationTableDef()
    for _ in range(10):
        setup_openapi(
            web.Application(),
            schema_path,
            operations,
            server_url="/api/",
            cache_create_schema_and_spec=True,
        )


def test_handle_all_create_schema_and_spec_errors(tmp_path):
    """
    Test for all schema errors.

    Args:
        tmp_path: (todo): write your description
    """
    invalid_json = tmp_path / "invalid_openapi.json"
    invalid_json.write_text('{"openapi": "3.')

    with pytest.raises(ConfigurationError):
        setup_openapi(web.Application(), invalid_json, OperationTableDef())


def test_ignore_non_http_view_methods():
    """
    Decorator methods that have a json serializable http headers

    Args:
    """
    operations = OperationTableDef()

    @operations.register
    class UserView(web.View):
        async def get(self) -> web.Response:
              """
              Return the response from the json.

              Args:
                  self: (todo): write your description
              """
            return web.json_response(True)

        @operations.register("update_user")
        async def patch(self) -> web.Response:
              """
              Replaces the given webhook.

              Args:
                  self: (todo): write your description
              """
            return web.json_response(True)

        async def get_user_or_404(self):
              """
              Get the user s error message.

              Args:
                  self: (todo): write your description
              """
            raise NotImplementedError

        def log_user(self, user):
            """
            Logs a user.

            Args:
                self: (todo): write your description
                user: (todo): write your description
            """
            raise NotImplementedError

    assert getattr(UserView, HANDLER_OPENAPI_MAPPING_KEY) == pmap(
        {"GET": UserView.get.__qualname__, "PATCH": "update_user"}
    )


def test_missed_schema_path_or_schema_and_spec():
    """
    Test if the schema exists. schema.

    Args:
    """
    with pytest.raises(ConfigurationError):
        setup_openapi(web.Application(), OperationTableDef())
