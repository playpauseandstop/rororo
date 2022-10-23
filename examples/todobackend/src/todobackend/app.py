from pathlib import Path
from typing import AsyncIterator, List, Union

from aiohttp import web
from aiohttp_middlewares import https_middleware
from aioredis.client import Redis

from rororo import setup_openapi, setup_settings
from rororo.settings import APP_SETTINGS_KEY
from todobackend import views
from todobackend.constants import APP_REDIS_KEY, APP_STORAGE_KEY
from todobackend.settings import Settings
from todobackend.storage import Storage


def create_app(
    argv: Union[List[str], None] = None,
    *,
    settings: Union[Settings, None] = None,
) -> web.Application:
    if settings is None:
        settings = Settings.from_environ()

    app = setup_openapi(
        setup_settings(
            web.Application(),
            settings,
            loggers=(
                "aiohttp",
                "aiohttp_middlewares",
                "rororo",
                "todobackend",
            ),
            remove_root_handlers=True,
        ),
        Path(__file__).parent / "openapi.yaml",
        views.operations,
        # Enable CORS requests from Swagger UI (http://localhost:8081) and
        # from Todo-Backend test-suite (http://www.todobackend.com) URLs
        cors_middleware_kwargs={
            "origins": ("http://localhost:8081", "http://www.todobackend.com")
        },
        # Allow caching schema and spec in tests
        cache_create_schema_and_spec=settings.is_test,
    )

    # Enable HTTPS middleware for production
    if settings.is_prod:
        app.middlewares.insert(0, https_middleware())

    app.cleanup_ctx.append(storage_context)
    return app


async def storage_context(app: web.Application) -> AsyncIterator[None]:
    settings: Settings = app[APP_SETTINGS_KEY]

    redis = app[APP_REDIS_KEY] = await Redis.from_url(
        settings.redis_url, decode_responses=True
    )
    app[APP_STORAGE_KEY] = Storage(
        redis=redis, data_key=settings.redis_data_key
    )

    yield

    await redis.close()
