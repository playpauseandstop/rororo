from pathlib import Path
from typing import List, Union

from aiohttp import web
from aiohttp_middlewares import (
    NON_IDEMPOTENT_METHODS,
    shield_middleware,
    timeout_middleware,
)

from hobotnica import views
from rororo import BaseSettings, setup_openapi, setup_settings


def create_app(
    argv: Union[List[str], None] = None,
    *,
    settings: Union[BaseSettings, None] = None,
) -> web.Application:
    if settings is None:
        settings = BaseSettings.from_environ()

    app = setup_openapi(
        setup_settings(
            web.Application(
                middlewares=(
                    shield_middleware(methods=NON_IDEMPOTENT_METHODS),
                    timeout_middleware(29.5),
                )
            ),
            settings,
            loggers=("aiohttp", "aiohttp_middlewares", "hobotnica", "rororo"),
            remove_root_handlers=True,
        ),
        Path(__file__).parent / "openapi.yaml",
        views.operations,
        cors_middleware_kwargs={"allow_all": True},
        cache_create_schema_and_spec=settings.is_test,
    )
    print(f"{app.middlewares=}")
    return app
