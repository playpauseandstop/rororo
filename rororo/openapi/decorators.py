from functools import wraps

from aiohttp import web

from .constants import (
    APP_OPENAPI_IS_VALIDATE_RESPONSE_KEY,
    REQUEST_OPENAPI_CONTEXT_KEY,
)
from .data import (
    OpenAPIContext,
    to_openapi_core_request,
    to_openapi_core_response,
)
from .security import validate_security
from .utils import (
    get_openapi_operation,
    get_openapi_schema,
    get_openapi_spec,
)
from .validators import (
    validate_request_parameters_and_body,
    validate_response_data,
)
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

            # Step 2. Validate security data if any
            security = validate_security(request, operation, oas=schema)

            # Step 3. Ensure that OpenAPI spec exists and convert aiohttp.web
            # request to openapi-core request
            spec = get_openapi_spec(config_dict)
            core_request = await to_openapi_core_request(request)

            # Step 4. Validate request parameters & body
            parameters, data = validate_request_parameters_and_body(
                spec, core_request
            )

            # Step 5. Provide OpenAPI context for the handler
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
                validate_response_data(
                    spec, core_request, to_openapi_core_response(response)
                )

            return response

        return decorator

    return wrapper
