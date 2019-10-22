from pathlib import Path
from typing import List

from aiohttp import web
from aiohttp_middlewares import cors_middleware, error_middleware

from rororo import setup_openapi
from . import views


def create_app(argv: List[str] = None) -> web.Application:
    app = web.Application(
        middlewares=(
            cors_middleware(allow_all=True),
            error_middleware(default_handler=views.error),
        )
    )

    setup_openapi(
        app,
        Path(__file__).parent / "openapi.yaml",
        views.operations,
        route_prefix="/api",
        is_validate_response=True,
    )

    return app
