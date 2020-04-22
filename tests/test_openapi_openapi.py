from aiohttp import web
from pyrsistent import pmap

from rororo import OperationTableDef
from rororo.openapi.constants import HANDLER_OPENAPI_MAPPING_KEY


def test_add_operations():
    operations = OperationTableDef()
    other = OperationTableDef()
    all_operations = OperationTableDef()

    @operations.register
    @all_operations.register
    async def create(request: web.Request) -> web.Response:
        return web.json_response(True, status=201)

    @other.register
    @all_operations.register
    async def update(request: web.Request) -> web.Response:
        return web.json_response(True)

    assert operations + other == all_operations
    assert operations != all_operations
    assert other != all_operations

    operations += other
    assert operations == all_operations
    assert other != all_operations


def test_ignore_non_http_view_methods():
    operations = OperationTableDef()

    @operations.register
    class UserView(web.View):
        async def get(self) -> web.Response:
            return web.json_response(True)

        @operations.register("update_user")
        async def patch(self) -> web.Response:
            return web.json_response(True)

        async def get_user_or_404(self):
            raise NotImplementedError

        def log_user(self, user):
            raise NotImplementedError

    assert getattr(UserView, HANDLER_OPENAPI_MAPPING_KEY) == pmap(
        {"GET": UserView.get.__qualname__, "PATCH": "update_user"}
    )
