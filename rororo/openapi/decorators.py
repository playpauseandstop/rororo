import types
from functools import wraps

from aiohttp import web
from openapi_core.shortcuts import validate_body, validate_parameters

from .contexts import OPENAPI_CONTEXT_REQUEST_KEY
from .data import (
    OpenAPIContext,
    to_openapi_core_request,
    to_openapi_parameters,
)
from .utils import get_openapi_operation, get_openapi_schema, get_openapi_spec
from ..annotations import Decorator, Handler


def openapi_operation(operation_id: str) -> Decorator:
    def wrapper(handler: Handler) -> Handler:
        @wraps(handler)
        async def decorator(request: web.Request) -> web.StreamResponse:
            app = request.app

            # Step 1. Ensure that OpenAPI schema exists as well as given
            # operation ID
            operation = get_openapi_operation(
                get_openapi_schema(app), operation_id
            )

            # Step 2. Ensure that OpenAPI spec exists and convert aiohttp.web
            # request to openapi-core request
            spec = get_openapi_spec(app)
            core_request = await to_openapi_core_request(request)

            # Step 3. Validate request parameters & body
            parameters = to_openapi_parameters(
                validate_parameters(spec, core_request)
            )
            valid_data = validate_body(spec, core_request)

            # TODO: Support request arrays as well
            data = None
            if valid_data is not None:
                data = types.MappingProxyType(vars(valid_data))

            # Step 4. Provide OpenAPI context for the handler
            request[OPENAPI_CONTEXT_REQUEST_KEY] = OpenAPIContext(
                request=request,
                app=app,
                operation=operation,
                parameters=parameters,
                data=data,
            )

            # Step 5. Validate response if needed
            # TODO: Implement response validation
            return await handler(request)

        return decorator

    return wrapper
