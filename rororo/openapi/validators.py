from aiohttp import web

from .constants import REQUEST_CORE_REQUEST_KEY, REQUEST_OPENAPI_CONTEXT_KEY
from .core_data import to_core_openapi_request, to_core_openapi_response
from .core_validators import validate_core_request, validate_core_response
from .data import OpenAPIContext
from .utils import get_openapi_spec


async def validate_request(request: web.Request) -> web.Request:
    config_dict = request.config_dict

    core_request = await to_core_openapi_request(request)
    request[REQUEST_CORE_REQUEST_KEY] = core_request

    security, parameters, data = validate_core_request(
        get_openapi_spec(config_dict), core_request
    )
    request[REQUEST_OPENAPI_CONTEXT_KEY] = OpenAPIContext(
        request=request,
        app=request.app,
        config_dict=config_dict,
        parameters=parameters,
        security=security,
        data=data,
    )

    return request


def validate_response(
    request: web.Request, response: web.StreamResponse
) -> web.StreamResponse:
    validate_core_response(
        get_openapi_spec(request.config_dict),
        request[REQUEST_CORE_REQUEST_KEY],
        to_core_openapi_response(response),
    )
    return response
