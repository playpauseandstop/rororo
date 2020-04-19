import attr
from aiohttp import web

from rororo import openapi_context, OperationTableDef
from .constants import APP_STORAGE_KEY
from .data import Todo
from .storage import Storage
from .validators import get_todo_or_404


operations = OperationTableDef()


@operations.register
async def create_todo(request: web.Request) -> web.Response:
    with openapi_context(request) as context:
        todo = Todo(
            title=context.data["title"], order=context.data.get("order") or 0
        )

    storage: Storage = request.config_dict[APP_STORAGE_KEY]
    await storage.create_todo(todo)

    return web.json_response(todo.to_api_dict(request=request), status=201)


@operations.register
async def delete_todo(request: web.Request) -> web.Response:
    storage: Storage = request.config_dict[APP_STORAGE_KEY]
    await storage.delete_todo(await get_todo_or_404(request))

    return web.json_response("")


@operations.register
async def delete_todos(request: web.Request) -> web.Response:
    storage: Storage = request.config_dict[APP_STORAGE_KEY]
    await storage.delete_todos()

    return web.json_response("")


@operations.register
async def list_todos(request: web.Request) -> web.Response:
    storage: Storage = request.config_dict[APP_STORAGE_KEY]
    todos = await storage.list_todos()

    return web.json_response(
        [item.to_api_dict(request=request) for item in todos]
    )


@operations.register
async def retrieve_todo(request: web.Request) -> web.Response:
    todo = await get_todo_or_404(request)
    return web.json_response(todo.to_api_dict(request=request))


@operations.register
async def update_todo(request: web.Request) -> web.Response:
    todo = await get_todo_or_404(request)

    with openapi_context(request) as context:
        next_todo = attr.evolve(todo, **context.data)

    storage: Storage = request.config_dict[APP_STORAGE_KEY]
    await storage.save_todo(next_todo)

    return web.json_response(next_todo.to_api_dict(request=request))
