import pytest
from aiohttp import BasicAuth
from hobotnica.app import create_app
from hobotnica.data import (
    GITHUB_PERSONAL_TOKEN,
    GITHUB_REPOSITORY,
    GITHUB_USERNAME,
)


REPOSITORIES_URL = "/api/repositories"
OWNER_REPOSITORIES_URL = f"{REPOSITORIES_URL}/{GITHUB_USERNAME}"
OWNER_ENV_URL = f"{OWNER_REPOSITORIES_URL}/env"
REPOSITORY_URL = f"{REPOSITORIES_URL}/{GITHUB_USERNAME}/{GITHUB_REPOSITORY}"
REPOSITORY_ENV_URL = f"{REPOSITORY_URL}/env"


async def test_create_repository_201(aiohttp_client):
    client = await aiohttp_client(create_app())
    response = await client.post(
        REPOSITORIES_URL,
        json={"owner": GITHUB_USERNAME, "name": GITHUB_REPOSITORY},
        headers={
            "X-GitHub-Username": GITHUB_USERNAME,
            "X-GitHub-Personal-Token": GITHUB_PERSONAL_TOKEN,
        },
    )
    assert response.status == 201


async def test_list_owner_repositories_200(aiohttp_client):
    client = await aiohttp_client(create_app())
    response = await client.get(
        OWNER_REPOSITORIES_URL,
        headers={
            "Authorization": BasicAuth(
                GITHUB_USERNAME, GITHUB_PERSONAL_TOKEN
            ).encode()
        },
    )

    assert response.status == 200
    data = await response.json()

    assert len(data) == 1
    assert data[0]["owner"] == GITHUB_USERNAME


@pytest.mark.parametrize(
    "invalid_headers",
    (
        {},
        {"Authorization": ""},
        {"Authorization": f"Bearer {GITHUB_PERSONAL_TOKEN}"},
        {"X-GitHub-Personal-Token": GITHUB_PERSONAL_TOKEN},
    ),
)
async def test_list_owner_repositories_401(aiohttp_client, invalid_headers):
    client = await aiohttp_client(create_app())
    response = await client.get(
        OWNER_REPOSITORIES_URL, headers=invalid_headers
    )

    assert response.status == 401
    assert response.headers["www-authenticate"] == "basic"
    assert await response.json() == {"detail": "Not authenticated"}


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
async def test_list_repositories_403_invalid_credentials(
    aiohttp_client, invalid_headers
):
    client = await aiohttp_client(create_app())
    response = await client.get(REPOSITORIES_URL, headers=invalid_headers)
    assert response.status == 403
    assert await response.json() == {"detail": "Invalid credentials"}


@pytest.mark.parametrize(
    "invalid_headers",
    (
        {"X-GitHub-Username": GITHUB_USERNAME},
        {"X-GitHub-Username": GITHUB_USERNAME, "X-GitHub-Personal-Token": ""},
        {"X-GitHub-Username": GITHUB_USERNAME, "Authorization": ""},
        {"X-GitHub-Username": GITHUB_USERNAME, "Authorization": "Bearer"},
    ),
)
async def test_list_repositories_403_not_authenticated(
    aiohttp_client, invalid_headers
):
    client = await aiohttp_client(create_app())
    response = await client.get(REPOSITORIES_URL, headers=invalid_headers)
    assert response.status == 403
    assert await response.json() == {"detail": "Not authenticated"}


@pytest.mark.parametrize(
    "invalid_headers",
    (
        {"X-GitHub-Personal-Token": GITHUB_PERSONAL_TOKEN},
        {"Authorization": f"Bearer {GITHUB_PERSONAL_TOKEN}"},
    ),
)
async def test_list_repositories_422(aiohttp_client, invalid_headers):
    client = await aiohttp_client(create_app())
    response = await client.get(REPOSITORIES_URL, headers=invalid_headers)
    assert response.status == 422
    assert await response.json() == {
        "detail": [
            {
                "loc": ["parameters", "X-GitHub-Username"],
                "message": "Parameter required",
            }
        ]
    }


async def test_retrieve_owner_env_200(aiohttp_client):
    client = await aiohttp_client(create_app())

    response = await client.get(
        OWNER_ENV_URL,
        headers={
            "Authorization": BasicAuth(
                GITHUB_USERNAME, GITHUB_PERSONAL_TOKEN
            ).encode()
        },
    )
    assert response.status == 200
    assert await response.json() == {
        "HOME": f"/home/{GITHUB_USERNAME}",
        "TIME_ZONE": "Europe/Kiev",
    }


async def test_retrieve_repository_200(aiohttp_client):
    client = await aiohttp_client(create_app())

    response = await client.get(
        REPOSITORY_URL,
        headers={
            "X-GitHub-Username": GITHUB_USERNAME,
            "X-GitHub-Personal-Token": GITHUB_PERSONAL_TOKEN,
            "Authorization": f"Bearer {GITHUB_PERSONAL_TOKEN}",
        },
    )
    assert response.status == 200

    data = await response.json()
    assert data["owner"] == GITHUB_USERNAME
    assert data["name"] == GITHUB_REPOSITORY


@pytest.mark.parametrize(
    "invalid_headers",
    (
        {},
        {"X-GitHub-Username": GITHUB_USERNAME},
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
async def test_retrieve_repository_403(aiohttp_client, invalid_headers):
    client = await aiohttp_client(create_app())

    response = await client.get(REPOSITORY_URL, headers=invalid_headers)
    assert response.status == 403
    assert await response.json() == {"detail": "Not authenticated"}


async def test_retrieve_repository_env_200(aiohttp_client):
    client = await aiohttp_client(create_app())

    response = await client.get(
        REPOSITORY_ENV_URL,
        headers={
            "X-GitHub-Username": GITHUB_USERNAME,
            "X-GitHub-Personal-Token": GITHUB_PERSONAL_TOKEN,
        },
    )
    assert response.status == 200
    assert await response.json() == {"LOCALE": "uk_UA.UTF-8"}
