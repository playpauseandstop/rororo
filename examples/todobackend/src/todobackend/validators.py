from aiohttp import web

from rororo import openapi_context
from rororo.openapi.exceptions import ObjectDoesNotExist

from .constants import APP_STORAGE_KEY
from .data import Todo
from .storage import Storage


async def get_todo_or_404(request: web.Request) -> Todo:
    storage: Storage = request.config_dict[APP_STORAGE_KEY]

    with openapi_context(request) as context:
        maybe_todo = await storage.get_todo(
            context.parameters.path["todo_uid"]
        )

    if maybe_todo:
        return maybe_todo

    raise ObjectDoesNotExist("Todo")
