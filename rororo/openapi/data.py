import types
from typing import Any, Dict, Optional

import attr
from aiohttp import web
from aiohttp.helpers import ChainMapProxy
from openapi_core.validation.request.models import RequestParameters
from openapi_core.wrappers.base import BaseOpenAPIRequest, BaseOpenAPIResponse

from ..annotations import DictStrAny, MappingStrAny, MappingStrStr


def immutable_dict_factory() -> MappingStrAny:
    """Shortcut to create immutable dict factory.

    For now, stick with ``types.MappingProxyType`` as immutable dict
    implementation.
    """
    return types.MappingProxyType({})


class OpenAPICoreRequest(BaseOpenAPIRequest):
    def __init__(self, request: web.Request, body: Optional[str]) -> None:
        self.request = request
        self.body = body

    @property
    def host_url(self) -> str:
        request = self.request
        return f"{request.scheme}://{request.host}"

    @property
    def method(self) -> str:
        return self.request.method.lower()

    @property
    def mimetype(self) -> str:
        return self.request.content_type

    @property
    def parameters(self) -> Dict[str, MappingStrStr]:
        request = self.request
        return {
            "path": request.match_info,
            "query": request.rel_url.query,
            "header": request.headers,
            "cookie": request.cookies,
        }

    @property
    def path(self) -> str:
        return self.request.path

    @property
    def path_pattern(self) -> str:
        info = self.request.match_info.route.get_info()
        formatter = info.get("formatter")
        return formatter if formatter is not None else info.get("path")


class OpenAPICoreResponse(BaseOpenAPIResponse):
    def __init__(self, response: web.StreamResponse) -> None:
        self.response = response

    @property
    def data(self) -> Optional[str]:
        response = self.response
        if isinstance(response, web.Response):
            return response.text
        return None

    @property
    def mimetype(self) -> str:
        return self.response.content_type

    @property
    def status_code(self) -> int:
        return self.response.status


@attr.dataclass(frozen=True, slots=True)
class OpenAPIOperation:
    #: Operation ID
    id: str

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


async def to_openapi_core_request(request: web.Request) -> OpenAPICoreRequest:
    """Convert aiohttp.web request to openapi-core request.

    Afterwards opeanpi-core request can be used for validation request data
    against spec.
    """
    body: Optional[str] = None
    if request.body_exists and request.can_read_body:
        body = await request.text()

    return OpenAPICoreRequest(request=request, body=body)


def to_openapi_core_response(
    response: web.StreamResponse,
) -> OpenAPICoreResponse:
    """Convert aiohttp.web response to openapi-core response."""
    return OpenAPICoreResponse(response)


def to_openapi_parameters(
    core_parameters: RequestParameters,
) -> OpenAPIParameters:
    """Convert openapi-core parameters to internal parameters instance."""
    return OpenAPIParameters(
        path=types.MappingProxyType(core_parameters["path"]),
        query=types.MappingProxyType(core_parameters["query"]),
        header=types.MappingProxyType(core_parameters["header"]),
        cookie=types.MappingProxyType(core_parameters["cookie"]),
    )
