from typing import Any

import attr
from aiohttp import web
from aiohttp.helpers import ChainMapProxy
from openapi_core.validation.request.datatypes import RequestParameters
from pyrsistent import pmap

from ..annotations import MappingStrAny


@attr.dataclass(frozen=True, slots=True)
class OpenAPIParameters:
    #: Path parameters
    path: MappingStrAny = attr.Factory(pmap)

    #: Query parameters
    query: MappingStrAny = attr.Factory(pmap)

    #: Parameters from headers
    header: MappingStrAny = attr.Factory(pmap)

    #: Cookie parameters
    cookie: MappingStrAny = attr.Factory(pmap)


@attr.dataclass(frozen=True, slots=True)
class OpenAPIContext:
    #: Request instance
    request: web.Request

    #: Application instance
    app: web.Application

    #: Config dict instance
    config_dict: ChainMapProxy

    #: Request parameters instance
    parameters: OpenAPIParameters = attr.Factory(OpenAPIParameters)

    #: Request security data
    security: MappingStrAny = attr.Factory(pmap)

    #: Request body data
    data: Any = None


def to_openapi_parameters(
    core_parameters: RequestParameters,
) -> OpenAPIParameters:
    """Convert openapi-core parameters to internal parameters instance."""
    return OpenAPIParameters(
        path=pmap(core_parameters.path),
        query=pmap(core_parameters.query),
        header=pmap(core_parameters.header),
        cookie=pmap(core_parameters.cookie),
    )
