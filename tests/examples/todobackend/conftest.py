try:
    from contextlib import asynccontextmanager
except ImportError:
    from async_generator import asynccontextmanager

import aioredis
import attr
import pytest

from todobackend.settings import Settings


@pytest.fixture()
def todobackend_data():
    return {"title": "New todo"}


@pytest.fixture()
def todobackend_redis():
    @asynccontextmanager
    async def factory(*, settings: Settings):
        redis = await aioredis.from_url(
            settings.redis_url, decode_responses=True
        )

        try:
            yield redis
        finally:
            keys = await redis.keys(f"{settings.redis_data_key}*")
            for key in keys:
                await redis.delete(key)

            await redis.close()

    return factory


@pytest.fixture()
def todobackend_settings():
    def factory() -> Settings:
        settings = Settings.from_environ()
        return attr.evolve(
            settings, redis_data_key=f"test:{settings.redis_data_key}"
        )

    return factory
