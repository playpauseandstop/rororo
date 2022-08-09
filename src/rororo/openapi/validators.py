from aiohttp import web

from rororo.openapi.constants import (
    REQUEST_CORE_REQUEST_KEY,
    REQUEST_OPENAPI_CONTEXT_KEY,
)
from rororo.openapi.core_data import (
    to_core_openapi_request,
    to_core_openapi_response,
)
from rororo.openapi.core_validators import (
    validate_core_request,
    validate_core_response,
)
from rororo.openapi.data import OpenAPIContext
from rororo.openapi.utils import get_openapi_spec, get_validate_email_kwargs


async def validate_request(request: web.Request) -> web.Request:
    config_dict = request.config_dict

    core_request = await to_core_openapi_request(request)
    request[REQUEST_CORE_REQUEST_KEY] = core_request

    security, parameters, data = validate_core_request(
        get_openapi_spec(config_dict),
        core_request,
        validate_email_kwargs=get_validate_email_kwargs(config_dict),
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
    config_dict = request.config_dict

    validate_core_response(
        get_openapi_spec(config_dict),
        request[REQUEST_CORE_REQUEST_KEY],
        to_core_openapi_response(response),
        validate_email_kwargs=get_validate_email_kwargs(config_dict),
    )
    return response
