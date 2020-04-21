from aiohttp import web
from aiohttp_middlewares import error_middleware, get_error_response
from aiohttp_middlewares.annotations import Middleware

from .constants import REQUEST_CORE_OPERATION_KEY
from .core_data import find_core_operation
from .validators import validate_request, validate_response
from ..annotations import DictStrAny, Handler


def openapi_middleware(
    *,
    is_validate_response: bool = True,
    use_error_middleware: bool = True,
    error_middleware_kwargs: DictStrAny = None
) -> Middleware:
    """Middleware to handle requests to handlers covered by OpenAPI schema.

    In most cases you don't need to add it to list of ``web.Application``
    middlewares as :func:`rororo.openapi.setup_openapi` will setup it for you,
    but if, for some reason, you don't want to call high order
    ``setup_openapi`` function, you'll need to add given middleware to your
    :class:`aiohttp.web.Applicaiton` manually.
    """

    error_middleware_instance = (
        error_middleware(**error_middleware_kwargs or {})
        if use_error_middleware
        else None
    )

    async def get_response(
        request: web.Request, handler: Handler
    ) -> web.StreamResponse:
        if error_middleware_instance is None:
            return await handler(request)
        return await error_middleware_instance(request, handler)

    @web.middleware
    async def middleware(
        request: web.Request, handler: Handler
    ) -> web.StreamResponse:
        # At first, check that given handler registered as OpenAPI operation
        # handler
        core_operation = find_core_operation(request, handler)
        if core_operation is None:
            return await get_response(request, handler)

        try:
            # Run actual `aiohttp.web` handler for requested operation
            request[REQUEST_CORE_OPERATION_KEY] = core_operation
            response = await get_response(
                await validate_request(request), handler
            )

            # For performance considerations it is useful to turn off
            # validating responses at production environment as unfortunately
            # it will need to do extra checks after response is ready
            if is_validate_response:
                validate_response(request, response)

            return response
        except Exception as err:
            return await get_error_response(
                request, err, **error_middleware_kwargs or {}
            )

    return middleware
