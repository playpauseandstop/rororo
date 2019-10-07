from typing import Any

import attr
from aiohttp import web

from .utils import immutable_dict_factory
from ..annotations import MappingStrAny


@attr.dataclass(frozen=True, slots=True)
class OpenAPIParameters:
    #: Path parameters
    path: MappingStrAny = attr.Factory(immutable_dict_factory)

    #: Query parameters
    query: MappingStrAny = attr.Factory(immutable_dict_factory)

    #: Parameters from headers
    header: MappingStrAny = attr.Factory(immutable_dict_factory)

    #: Cookie parameters
    cookie: MappingStrAny = attr.Factory(immutable_dict_factory)


@attr.dataclass(frozen=True, slots=True)
class OpenAPIContext:
    #: Operation ID from OpenAPI Schema
    operation_id: str

    #: Request instance
    request: web.Request

    #: Application instance
    app: web.Application

    #: Request parameters instance
    parameters: OpenAPIParameters = attr.Factory(OpenAPIParameters)

    #: Request security data
    security: MappingStrAny = attr.Factory(immutable_dict_factory)

    #: Request body data
    data: Any = None
