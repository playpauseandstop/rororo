from typing import Optional

from aiohttp import hdrs, web
from aiohttp.payload import IOBasePayload, Payload
from openapi_core.schema.operations.models import Operation
from openapi_core.schema.specs.models import Spec
from openapi_core.validation.request.datatypes import (
    OpenAPIRequest,
    RequestParameters,
)
from openapi_core.validation.response.datatypes import OpenAPIResponse
from yarl import URL

from .constants import HANDLER_OPENAPI_MAPPING_KEY
from .exceptions import OperationError
from .utils import get_openapi_spec
from ..annotations import Handler


def find_core_operation(
    request: web.Request, handler: Handler
) -> Optional[Operation]:
    mapping = getattr(handler, HANDLER_OPENAPI_MAPPING_KEY, None)
    if not mapping:
        return None

    operation_id = mapping.get(request.method) or mapping.get(hdrs.METH_ANY)
    if operation_id is None:
        return None

    try:
        return get_core_operation(
            get_openapi_spec(request.config_dict), operation_id
        )
    except OperationError:
        return None


def get_core_operation(spec: Spec, operation_id: str) -> Operation:
    for path in spec.paths.values():
        for operation in path.operations.values():
            if operation.operation_id == operation_id:
                return operation
    raise OperationError(
        f"Unable to find operation '{operation_id}' in given OpenAPI spec"
    )


def get_full_url_pattern(request: web.Request) -> str:
    """Get full URL pattern for given :class:`aiohttp.web.Request` instance."""
    full_url: URL = request.url.with_path(get_path_pattern(request))
    return full_url.human_repr()


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


async def to_core_openapi_request(request: web.Request) -> OpenAPIRequest:
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