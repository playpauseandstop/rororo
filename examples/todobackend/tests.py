import uuid

try:
    from contextlib import asynccontextmanager
except ImportError:
    from async_generator import asynccontextmanager

import attr
import pyrsistent
import pytest
from aioredis import create_redis
from todobackend.app import create_app
from todobackend.data import Todo
from todobackend.settings import Settings
from todobackend.storage import Storage
from yarl import URL


TEST_TITLE = "New todo"
URL_TODOS = URL("/todos/")


@pytest.fixture
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


@pytest.fixture
def todobackend_settings():
    def factory() -> Settings:
        settings = Settings.from_environ()
        return attr.evolve(
            settings, redis_data_key=f"test:{settings.redis_data_key}"
        )

    return factory


async def test_flow(aiohttp_client, todobackend_redis, todobackend_settings):
    settings = todobackend_settings()
    async with todobackend_redis(settings=settings):
        client = await aiohttp_client(create_app(settings=settings))

        response = await client.get(URL_TODOS)
        assert response.status == 200
        assert await response.json() == []

        response = await client.post(URL_TODOS, json={"title": TEST_TITLE})
        assert response.status == 201
        data = await response.json()
        assert data["title"] == TEST_TITLE

        url = URL(data["url"]).relative()

        response = await client.get(url)
        assert response.status == 200
        assert await response.json() == data

        response = await client.get(URL_TODOS)
        assert response.status == 200
        assert await response.json() == [data]

        response = await client.patch(url, json={"completed": True})
        assert response.status == 200
        assert await response.json() == {**data, "completed": True}

        response = await client.delete(url)
        assert response.status == 200

        response = await client.get(url)
        assert response.status == 404

        response = await client.get(URL_TODOS)
        assert response.status == 200
        assert await response.json() == []


async def test_openapi_schema(aiohttp_client, todobackend_settings):
    settings = todobackend_settings()
    client = await aiohttp_client(create_app(settings=settings))
    response = await client.get(URL_TODOS / "openapi.yaml")
    assert response.status == 200


async def test_storage(todobackend_redis, todobackend_settings):
    settings = todobackend_settings()
    async with todobackend_redis(settings=settings) as redis:
        storage = Storage(redis=redis, data_key=settings.redis_data_key)

        assert await storage.list_todos() == []

        todo = Todo(title=TEST_TITLE)
        await storage.create_todo(todo)
        assert await storage.list_todos() == pyrsistent.v(todo)
        assert await storage.get_todo(todo.uid) == todo

        completed_todo = attr.evolve(todo, completed=True)
        assert await storage.save_todo(completed_todo) != todo
        assert await storage.get_todo(todo.uid) == completed_todo

        assert await storage.delete_todo(todo) == 1
        assert await storage.get_todo(todo.uid) is None

        await storage.create_todo(todo)
        await storage.create_todo(
            attr.evolve(completed_todo, uid=uuid.uuid4())
        )
        assert await storage.delete_todos() == 2

        assert await storage.delete_todo(todo) == 0
        assert await storage.delete_todos() == 0
