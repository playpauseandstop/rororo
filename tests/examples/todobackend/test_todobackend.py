import pytest
from todobackend.app import create_app
from yarl import URL


FAKE_UID = "b3f8d6d7-f4a5-44bb-ba36-85a6579b63c0"
URL_TODOS = URL("/todos/")


async def test_flow(
    aiohttp_client, todobackend_data, todobackend_redis, todobackend_settings
):
    settings = todobackend_settings()
    async with todobackend_redis(settings=settings):
        client = await aiohttp_client(create_app(settings=settings))

        response = await client.get(URL_TODOS)
        assert response.status == 200
        assert await response.json() == []

        title = todobackend_data["title"]
        response = await client.post(URL_TODOS, json={"title": title})
        assert response.status == 201
        data = await response.json()
        assert data["title"] == title

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


@pytest.mark.parametrize(
    "route_name, kwargs, expected",
    (
        ("create_todo", {}, URL_TODOS),
        ("list_todos", {}, URL_TODOS),
        ("TodosView.delete", {}, URL_TODOS),
        ("todo.delete", {"todo_uid": FAKE_UID}, URL_TODOS / FAKE_UID),
        ("todo.get", {"todo_uid": FAKE_UID}, URL_TODOS / FAKE_UID),
        ("todo.patch", {"todo_uid": FAKE_UID}, URL_TODOS / FAKE_UID),
    ),
)
async def test_url(route_name, kwargs, expected):
    app = create_app()
    assert app.router[route_name].url_for(**kwargs) == expected
