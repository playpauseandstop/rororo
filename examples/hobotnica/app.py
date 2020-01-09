from pathlib import Path
from typing import List

from aiohttp import web
from aiohttp_middlewares import cors_middleware, error_middleware

from rororo import BaseSettings, setup_openapi, setup_settings
from . import views


def create_app(
    argv: List[str] = None, *, settings: BaseSettings = None
) -> web.Application:
    if settings is None:
        settings = BaseSettings()

    return setup_openapi(
        setup_settings(
            web.Application(
                middlewares=(
                    cors_middleware(allow_all=True),
                    error_middleware(default_handler=views.error),
                )
            ),
            settings,
            loggers=("aiohttp", "aiohttp_middlewares", "hobotnica", "rororo"),
            remove_root_handlers=True,
        ),
        Path(__file__).parent / "openapi.yaml",
        views.operations,
        route_prefix="/api",
        is_validate_response=True,
    )
