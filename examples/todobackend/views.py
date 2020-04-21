import attr
from aiohttp import web

from rororo import openapi_context, OperationTableDef
from .constants import APP_STORAGE_KEY
from .data import Todo
from .storage import Storage
from .validators import get_todo_or_404


operations = OperationTableDef()


@operations.register
class TodosView(web.View):
    async def delete(self) -> web.Response:
        storage: Storage = self.request.config_dict[APP_STORAGE_KEY]
        await storage.delete_todos()

        return web.json_response("")

    async def get(self) -> web.Response:
        request = self.request

        storage: Storage = request.config_dict[APP_STORAGE_KEY]
        todos = await storage.list_todos()

        return web.json_response(
            [item.to_api_dict(request=request) for item in todos]
        )

    async def post(self) -> web.Response:
        request = self.request

        with openapi_context(request) as context:
            todo = Todo(
                title=context.data["title"],
                order=context.data.get("order") or 0,
            )

        storage: Storage = request.config_dict[APP_STORAGE_KEY]
        await storage.create_todo(todo)

        return web.json_response(todo.to_api_dict(request=request), status=201)


@operations.register("todo")
class TodoView(web.View):
    async def delete(self) -> web.Response:
        request = self.request

        storage: Storage = request.config_dict[APP_STORAGE_KEY]
        await storage.delete_todo(await get_todo_or_404(request))

        return web.json_response("")

    async def get(self) -> web.Response:
        request = self.request
        todo = await get_todo_or_404(request)
        return web.json_response(todo.to_api_dict(request=request))

    async def patch(self) -> web.Response:
        request = self.request
        todo = await get_todo_or_404(request)

        with openapi_context(request) as context:
            next_todo = attr.evolve(todo, **context.data)

        storage: Storage = request.config_dict[APP_STORAGE_KEY]
        await storage.save_todo(next_todo)

        return web.json_response(next_todo.to_api_dict(request=request))
