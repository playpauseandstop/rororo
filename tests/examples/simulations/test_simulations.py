import copy

import pytest
from simulations.app import create_app
from simulations.storage import DEFAULT_STORAGE
from yarl import URL


TEST_STORAGE_MISSING_VALUES = [
    {
        "dataset_id": "test_dataset_id",
        "model_id": "test_model_id",
        "simulation_id": "4c972a77-e86c-4d02-856f-dc1f3d2b9f5a",
        "simulation_status": "CREATED",
    }
]
TEST_URL = URL("/simulations")


@pytest.mark.parametrize(
    "data", (DEFAULT_STORAGE[0], TEST_STORAGE_MISSING_VALUES[0])
)
async def test_create_simulation(aiohttp_client, data):
    client = await aiohttp_client(create_app())
    response = await client.post(TEST_URL, json=data)
    assert response.status == 201
    assert await response.json() == data


@pytest.mark.parametrize(
    "storage",
    (None, copy.deepcopy(DEFAULT_STORAGE), TEST_STORAGE_MISSING_VALUES),
)
async def test_list_simulations(aiohttp_client, storage):
    app = create_app()
    app["storage"] = storage

    client = await aiohttp_client(app)
    response = await client.get(TEST_URL)
    assert response.status == 200
    assert await response.json() == storage
