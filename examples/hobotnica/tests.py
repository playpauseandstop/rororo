import pytest
from aiohttp import BasicAuth
from hobotnica.app import create_app
from hobotnica.data import (
    GITHUB_PERSONAL_TOKEN,
    GITHUB_REPOSITORY,
    GITHUB_USERNAME,
)


REPOSITORIES_URL = "/api/repositories"
REPOSITORY_URL = f"{REPOSITORIES_URL}/{GITHUB_USERNAME}/{GITHUB_REPOSITORY}"


@pytest.mark.parametrize(
    "headers",
    (
        {
            "X-GitHub-Username": GITHUB_USERNAME,
            "X-GitHub-Personal-Token": GITHUB_PERSONAL_TOKEN,
        },
        {
            "X-GitHub-Username": GITHUB_USERNAME,
            "Authorization": f"Bearer {GITHUB_PERSONAL_TOKEN}",
        },
    ),
)
async def test_list_repositories_200(aiohttp_client, headers):
    client = await aiohttp_client(create_app())
    response = await client.get(REPOSITORIES_URL, headers=headers)

    assert response.status == 200
    data = await response.json()

    assert len(data) == 1
    assert data[0]["owner"] == GITHUB_USERNAME


@pytest.mark.parametrize(
    "invalid_headers",
    (
        {
            "X-GitHub-Username": GITHUB_USERNAME[::-1],
            "X-GitHub-Personal-Token": GITHUB_PERSONAL_TOKEN,
        },
        {
            "X-GitHub-Username": GITHUB_USERNAME,
            "X-GitHub-Personal-Token": "invalid",
        },
        {
            "X-GitHub-Username": GITHUB_USERNAME[::-1],
            "Authorization": f"Bearer {GITHUB_PERSONAL_TOKEN}",
        },
        {
            "X-GitHub-Username": GITHUB_USERNAME,
            "Authorization": "Bearer invalid",
        },
    ),
)
async def test_list_repositories_401(aiohttp_client, invalid_headers):
    client = await aiohttp_client(create_app())
    response = await client.get(REPOSITORIES_URL, headers=invalid_headers)
    assert response.status == 401
    assert await response.json() == {"detail": "Invalid credentials."}


@pytest.mark.parametrize(
    "invalid_headers",
    (
        {},
        {"X-GitHub-Username": ""},
        {"X-GitHub-Personal-Token": ""},
        {"Authorization": ""},
        {"X-GitHub-Username": GITHUB_USERNAME},
        {"X-GitHub-Personal-Token": GITHUB_PERSONAL_TOKEN},
        {"Authorization": f"Bearer {GITHUB_PERSONAL_TOKEN}"},
        {"X-GitHub-Username": GITHUB_USERNAME, "X-GitHub-Personal-Token": ""},
        {"X-GitHub-Username": GITHUB_USERNAME, "Authorization": ""},
        {"X-GitHub-Username": GITHUB_USERNAME, "Authorization": "Bearer"},
    ),
)
async def test_list_repositories_500(aiohttp_client, invalid_headers):
    client = await aiohttp_client(create_app())
    response = await client.get(REPOSITORIES_URL, headers=invalid_headers)
    assert response.status == 500

    data = await response.json()
    assert len(data) == 1
    assert "detail" in data


@pytest.mark.parametrize(
    "headers",
    (
        {
            "X-GitHub-Username": GITHUB_USERNAME,
            "Authorization": BasicAuth(
                GITHUB_USERNAME, GITHUB_PERSONAL_TOKEN
            ).encode(),
        },
        {
            "X-GitHub-Username": GITHUB_USERNAME,
            "X-GitHub-Personal-Token": GITHUB_PERSONAL_TOKEN,
            "Authorization": f"Bearer {GITHUB_PERSONAL_TOKEN}",
        },
    ),
)
async def test_retrieve_repository_200(aiohttp_client, headers):
    client = await aiohttp_client(create_app())

    response = await client.get(REPOSITORY_URL, headers=headers)
    assert response.status == 200

    data = await response.json()
    assert data["owner"] == GITHUB_USERNAME
    assert data["name"] == GITHUB_REPOSITORY
