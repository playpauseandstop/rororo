from contextlib import suppress
from functools import wraps

from aiohttp import web

from .contexts import OPENAPI_CONTEXT_REQUEST_KEY
from .data import OpenAPIContext
from ..annotations import Decorator, Handler


def openapi_operation(operation_id: str) -> Decorator:
    def wrapper(handler: Handler) -> Handler:
        @wraps(handler)
        async def decorator(request: web.Request) -> web.StreamResponse:
            data = None
            with suppress(ValueError):
                data = await request.json()

            request[OPENAPI_CONTEXT_REQUEST_KEY] = OpenAPIContext(
                operation_id=operation_id,
                request=request,
                app=request.app,
                data=data,
            )

            return await handler(request)

        return decorator

    return wrapper
