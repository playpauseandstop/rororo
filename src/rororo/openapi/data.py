"""
===================
rororo.openapi.data
===================

Provide structures for OpenAPI data.

"""

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
    """All data associated with current request to OpenAPI handler.

    Contains only valid parameters, security data & request body data.
    Example bellow illustrates how to work with context data,

    .. code-block:: python

        from rororo import get_openapi_context
        from rororo.openapi.exceptions import InvalidCredentials


        async def create_user(request: web.Request) -> web.Response:
            context = get_openapi_context(request)

            # Authenticate current user (accessing security data)
            if not authenticate(api_key=context.security["apiKey"]):
                raise InvalidCredentials()

            # Add new user (accessing request body data)
            async with request.config_dict["db"].acquire() as conn:
                user = await create_user(
                    conn,
                    email=context.data["email"],
                    password=context.data["password"],
                )

            # Return response due to query string param
            # (accessing parameters data)
            if context.parameters.query["login"]:
                return web.json_response(
                    request.app.router["login"].url_for()
                )

            return web.json_response(user.to_api_dict())

    """

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
