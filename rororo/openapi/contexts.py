from contextlib import contextmanager
from typing import Iterator

from aiohttp import web

from .data import OpenAPIContext
from .utils import get_openapi_context


@contextmanager
def openapi_context(request: web.Request) -> Iterator[OpenAPIContext]:
    """Context manager to access valid OpenAPI data for given request.

    If request validation done well and request to OpenAPI operation view
    handler is valid one, view handler may need to use request data for its
    needs. To achieve it use given context manager as,

    .. code-block:: python

        from rororo import openapi_context, OperationTableDef

        operations = OperationTableDef()


        @operations.register
        async def hello_world(request: web.Request) -> web.Response:
            with openapi_context(request) as context:
                ...

    If using context managers inside of view handlers considered as unwanted,
    there is an other option in
    :func:`rororo.openapi.get_openapi_context` function.
    """
    yield get_openapi_context(request)
