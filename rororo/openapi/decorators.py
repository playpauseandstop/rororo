from functools import wraps

from aiohttp import web

from .constants import (
    APP_OPENAPI_IS_VALIDATE_RESPONSE_KEY,
    REQUEST_OPENAPI_CONTEXT_KEY,
)
from .data import (
    OpenAPIContext,
    to_core_openapi_request,
    to_core_openapi_response,
)
from .utils import (
    get_openapi_operation,
    get_openapi_schema,
    get_openapi_spec,
)
from .validators import validate_request, validate_response
from ..annotations import Decorator, Handler


def openapi_operation(operation_id: str) -> Decorator:
    """
    Hidden decorator, that allows :class:`rororo.openapi.OperationTableDef`
    to really ensure that registered view handler will receive data, that is
    valid against requested OpenAPI schema.
    """

    def wrapper(handler: Handler) -> Handler:
        @wraps(handler)
        async def decorator(request: web.Request) -> web.StreamResponse:
            app = request.app
            config_dict = request.config_dict

            # Step 1. Ensure that OpenAPI schema exists as well as given
            # operation ID
            schema = get_openapi_schema(config_dict)
            operation = get_openapi_operation(schema, operation_id)

            # Step 2. Ensure that OpenAPI spec exists and convert aiohttp.web
            # request to openapi-core request
            spec = get_openapi_spec(config_dict)
            core_request = await to_core_openapi_request(request)

            # Step 3. Validate request parameters, security & body
            security, parameters, data = validate_request(spec, core_request)

            # Step 4. Provide OpenAPI context for the handler
            request[REQUEST_OPENAPI_CONTEXT_KEY] = OpenAPIContext(
                request=request,
                app=app,
                config_dict=config_dict,
                operation=operation,
                parameters=parameters,
                data=data,
                security=security,
            )

            # Step 5. Validate response if needed
            response = await handler(request)
            if config_dict[APP_OPENAPI_IS_VALIDATE_RESPONSE_KEY]:
                validate_response(
                    spec, core_request, to_core_openapi_response(response)
                )

            return response

        return decorator

    return wrapper
