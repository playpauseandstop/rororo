from contextlib import contextmanager
from typing import Iterator

from aiohttp import web

from .constants import OPENAPI_CONTEXT_REQUEST_KEY
from .data import OpenAPIContext


@contextmanager
def openapi_context(request: web.Request) -> Iterator[OpenAPIContext]:
    yield request[OPENAPI_CONTEXT_REQUEST_KEY]
