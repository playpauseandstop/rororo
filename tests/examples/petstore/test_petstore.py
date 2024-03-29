import pytest

from petstore.app import create_app
from petstore.data import Pet


TEST_PET_NAME = "Test Pet"
TEST_PET = Pet(id=1, name=TEST_PET_NAME, tag=None)

ADD_PET_JSON = {"name": TEST_PET_NAME}


async def test_add_pet_200(aiohttp_client):
    client = await aiohttp_client(create_app())
    response = await client.post("/api/pets", json=ADD_PET_JSON)
    assert response.status == 200
    assert await response.json() == {
        "id": 1,
        "name": TEST_PET_NAME,
    }


@pytest.mark.parametrize(
    "invalid_data, expected",
    (
        (None, [["body"]]),
        ({}, [["body", "name"]]),
        ({"name": None}, [["body", "name"]]),
        ({"name": 42}, [["body", "name"]]),
    ),
)
async def test_add_pet_422(aiohttp_client, invalid_data, expected):
    client = await aiohttp_client(create_app())
    response = await client.post("/api/pets", json=invalid_data)
    assert response.status == 422

    data = await response.json()
    assert [item["loc"] for item in data["detail"]] == expected


async def test_delete_pet(aiohttp_client):
    client = await aiohttp_client(create_app())
    await client.post("/api/pets", json=ADD_PET_JSON)

    response = await client.delete("/api/pets/1")
    assert response.status == 204

    response = await client.get("/api/pets")
    assert response.status == 200
    assert await response.json() == []


async def test_delete_pet_does_not_exist(aiohttp_client):
    client = await aiohttp_client(create_app())
    response = await client.delete("/api/pets/1")
    assert response.status == 404
    assert await response.json() == {"detail": "Requested Pet not found"}


async def test_get_pet(aiohttp_client):
    client = await aiohttp_client(create_app())
    await client.post("/api/pets", json=ADD_PET_JSON)

    response = await client.get("/api/pets/1")
    assert response.status == 200
    assert await response.json() == {
        "id": 1,
        "name": TEST_PET_NAME,
    }


async def test_get_pet_does_not_exist(aiohttp_client):
    client = await aiohttp_client(create_app())
    response = await client.get("/api/pets/1")
    assert response.status == 404
    assert await response.json() == {"detail": "Requested Pet not found"}


async def test_list_pets(aiohttp_client):
    client = await aiohttp_client(create_app())
    await client.post("/api/pets", json=ADD_PET_JSON)

    response = await client.get("/api/pets")
    assert response.status == 200
    assert await response.json() == [{"id": 1, "name": TEST_PET_NAME}]


async def test_list_pets_empty(aiohttp_client):
    client = await aiohttp_client(create_app())
    response = await client.get("/api/pets")
    assert response.status == 200
    assert await response.json() == []
