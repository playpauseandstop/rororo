from pathlib import Path
from typing import List

from aiohttp import web
from aiohttp_middlewares import cors_middleware, error_middleware

from rororo import setup_openapi, setup_settings
from . import views
from .settings import Settings


def create_app(
    argv: List[str] = None, *, settings: Settings = None
) -> web.Application:
    """Create aiohttp applicaiton for OpenAPI 3 Schema.

    The ``petstore-expanded.yaml`` schema taken from OpenAPI 3 Specification
    examples directory and used inside the app without modifications besides
    changing default server URL to use.

    As pets storage is a simple list, it will be cleared on each application
    shutdown.

    This aiohttp application is ready to be run as:

    .. code-block:: bash

        python -m aiohttp.web petstore.app:create_app

    After application is running, feel free to use Swagger UI to check the
    results. The OpenAPI schema will be available at:
    http://localhost:8080/api/openapi.yaml

    To ensure that Swagger UI been able to make requests to the PetStore
    example app CORS headers allowed for all requests. **Please, avoid
    enabling CORS headers for all requests at production.**
    """
    # Instantiate settings
    if settings is None:
        settings = Settings()

    # Create new aiohttp application with CORS & error middlewares
    app = web.Application(
        middlewares=(
            # CORS middleware should be the first one as it ensures that every
            # aiohttp response use proper CORS headers
            cors_middleware(allow_all=True),
            # It's good practice to enable error middleware right after the
            # CORS one to catch as many errors as possible
            error_middleware(),
        )
    )

    # Store the settings within the app
    setup_settings(
        app,
        settings,
        loggers=("aiohttp", "aiohttp_middlewares", "petstore", "rororo"),
        remove_root_handlers=True,
    )

    # Create the "storage" for the pets
    app[settings.pets_app_key] = []

    # Setup OpenAPI schema support for aiohttp application
    setup_openapi(
        # Where first param is an application instance
        app,
        # Second is path to OpenAPI 3 Schema
        Path(__file__).parent / "petstore-expanded.yaml",
        # And after list of operations
        views.operations,
        # Need to add route prefix if server URL in OpenAPI schema ended with
        # a path, like "http://localhost:8080/api"
        route_prefix="/api",
    )

    return app
