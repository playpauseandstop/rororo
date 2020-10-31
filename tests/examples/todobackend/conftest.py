try:
    from contextlib import asynccontextmanager
except ImportError:
    from async_generator import asynccontextmanager

import attr
import pytest
from aioredis import create_redis
from todobackend.settings import Settings


@pytest.fixture()
def todobackend_data():
    return {"title": "New todo"}


@pytest.fixture()
def todobackend_redis():
    @asynccontextmanager
    async def factory(*, settings: Settings):
        redis = await create_redis(settings.redis_url, encoding="utf-8")

        try:
            yield redis
        finally:
            keys = await redis.keys(f"{settings.redis_data_key}*")
            for key in keys:
                await redis.delete(key)

            redis.close()
            await redis.wait_closed()

    return factory


@pytest.fixture()
def todobackend_settings():
    def factory() -> Settings:
        settings = Settings.from_environ()
        return attr.evolve(
            settings, redis_data_key=f"test:{settings.redis_data_key}"
        )

    return factory
