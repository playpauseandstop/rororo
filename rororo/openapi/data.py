import types
from typing import Any, Optional

import attr
from aiohttp import web
from aiohttp.helpers import ChainMapProxy
from aiohttp.payload import IOBasePayload, Payload
from openapi_core.validation.request.datatypes import (
    OpenAPIRequest,
    RequestParameters,
)
from openapi_core.validation.response.datatypes import OpenAPIResponse

from ..annotations import DictStrAny, MappingStrAny


def immutable_dict_factory() -> MappingStrAny:
    """Shortcut to create immutable dict factory.

    For now, stick with ``types.MappingProxyType`` as immutable dict
    implementation.
    """
    return types.MappingProxyType({})


@attr.dataclass(frozen=True, slots=True)
class OpenAPIOperation:
    #: Operation ID
    id: str  # noqa: A003

    #: Operation path
    path: str

    #: Operation method
    method: str

    #: Full operation schema
    schema: DictStrAny

    @property
    def route_name(self) -> str:
        """Ensure safe route name for operation ID.

        OpenAPI schema allows to use spaces for operation ID, while aiohttp
        disallows them. Cause of that replace all spaces with dashes.
        """
        return self.id.replace(" ", "-")


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
    #: Request instance
    request: web.Request

    #: Application instance
    app: web.Application

    #: Config dict instance
    config_dict: ChainMapProxy

    #: Operation instance
    operation: OpenAPIOperation

    #: Request parameters instance
    parameters: OpenAPIParameters = attr.Factory(OpenAPIParameters)

    #: Request security data
    security: MappingStrAny = attr.Factory(immutable_dict_factory)

    #: Request body data
    data: Any = None


def get_full_url_pattern(request: web.Request) -> str:
    return str(request.url.with_path(get_path_pattern(request)))


def get_path_pattern(request: web.Request) -> str:
    """Get path pattern for given :class:`aiohttp.web.Request` instance.

    When current handler is a dynamic route: use formatter, otherwise use
    path from route info.
    """
    info = request.match_info.route.get_info()
    formatter = info.get("formatter")
    return (  # type: ignore
        formatter if formatter is not None else info.get("path")
    )


async def to_core_openapi_request(request: web.Request,) -> OpenAPIRequest:
    """Convert aiohttp.web request to openapi-core request.

    Afterwards opeanpi-core request can be used for validation request data
    against spec.
    """
    body: Optional[bytes] = None
    if request.body_exists and request.can_read_body:
        body = await request.read()

    return OpenAPIRequest(
        full_url_pattern=get_full_url_pattern(request),
        method=request.method.lower(),
        body=body,
        mimetype=request.content_type,
        parameters=to_core_request_parameters(request),
    )


def to_core_openapi_response(response: web.StreamResponse) -> OpenAPIResponse:
    """Convert aiohttp.web response to openapi-core response."""
    return OpenAPIResponse(
        data=to_core_openapi_response_data(response),
        status_code=response.status,
        mimetype=response.content_type,
    )


def to_core_openapi_response_data(
    response: web.StreamResponse,
) -> Optional[bytes]:
    if isinstance(response, web.Response):
        body = response.body
        if not body:
            return None

        # TODO: Find better way to provide response from payload
        if isinstance(body, IOBasePayload):
            return body._value.getvalue()  # type: ignore

        if isinstance(body, Payload):
            return body._value  # type: ignore

        return body
    return None


def to_core_request_parameters(request: web.Request) -> RequestParameters:
    return RequestParameters(
        query=request.rel_url.query,
        header=request.headers,
        cookie=request.cookies,
        path=request.match_info,
    )


def to_openapi_parameters(
    core_parameters: RequestParameters,
) -> OpenAPIParameters:
    """Convert openapi-core parameters to internal parameters instance."""
    return OpenAPIParameters(
        path=types.MappingProxyType(core_parameters.path),
        query=types.MappingProxyType(core_parameters.query),
        header=types.MappingProxyType(core_parameters.header),
        cookie=types.MappingProxyType(core_parameters.cookie),
    )
