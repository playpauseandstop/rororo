import pytest
from aiohttp import BasicAuth
from hobotnica.app import create_app
from hobotnica.data import (
    GITHUB_PERSONAL_TOKEN,
    GITHUB_REPOSITORY,
    GITHUB_USERNAME,
)
from yarl import URL


URL_REFERENCES = URL("/api/public/references")
URL_REPOSITORIES = URL("/api/repositories")
URL_FAVORITES_REPOSITORIES = URL_REPOSITORIES / "favorites"
URL_OWNER_REPOSITORIES = URL_REPOSITORIES / GITHUB_USERNAME
URL_OWNER_REPOSITORIES_ENV = URL_OWNER_REPOSITORIES / "env"
URL_REPOSITORY = URL_REPOSITORIES / GITHUB_USERNAME / GITHUB_REPOSITORY
URL_REPOSITORY_ENV = URL_REPOSITORY / "env"


async def test_create_repository_201(aiohttp_client):
      """
      Create a repository repository.

      Args:
          aiohttp_client: (todo): write your description
      """
    client = await aiohttp_client(create_app())
    response = await client.post(
        URL_REPOSITORIES,
        json={"owner": GITHUB_USERNAME, "name": GITHUB_REPOSITORY},
        headers={
            "X-GitHub-Username": GITHUB_USERNAME,
            "X-GitHub-Personal-Token": GITHUB_PERSONAL_TOKEN,
        },
    )
    assert response.status == 201


async def test_list_all_references(aiohttp_client):
      """
      Test all references.

      Args:
          aiohttp_client: (todo): write your description
      """
    client = await aiohttp_client(create_app())
    response = await client.get(URL_REFERENCES)
    assert response.status == 200
    assert await response.json() == {
        "default_env": {"CI": "1", "HOBOTNICA": "1"}
    }


async def test_list_favorites_repositories_204(aiohttp_client):
      """
      List all repositories in a repository repositories.

      Args:
          aiohttp_client: (todo): write your description
      """
    client = await aiohttp_client(create_app())
    response = await client.get(
        URL_FAVORITES_REPOSITORIES,
        headers={
            "X-GitHub-Username": GITHUB_USERNAME,
            "X-GitHub-Personal-Token": GITHUB_PERSONAL_TOKEN,
        },
    )
    assert response.status == 204
    assert response.headers["X-Order"] == "date"


async def test_list_owner_repositories_200(aiohttp_client):
      """
      Gets a list of owner in - memory owner.

      Args:
          aiohttp_client: (todo): write your description
      """
    client = await aiohttp_client(create_app())
    response = await client.get(
        URL_OWNER_REPOSITORIES,
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
      """
      Gets the owner of the owner.

      Args:
          aiohttp_client: (todo): write your description
          invalid_headers: (str): write your description
      """
    client = await aiohttp_client(create_app())
    response = await client.get(
        URL_OWNER_REPOSITORIES, headers=invalid_headers
    )

    assert response.status == 401
    assert response.headers["www-authenticate"] == "basic"
    assert await response.json() == {"detail": "Not authenticated"}


async def test_list_owner_repositories_422(aiohttp_client):
      """
      Gets the owner of owner.

      Args:
          aiohttp_client: (todo): write your description
      """
    client = await aiohttp_client(create_app())
    response = await client.get(
        URL_REPOSITORIES / "ab",
        headers={
            "Authorization": BasicAuth(
                GITHUB_USERNAME, GITHUB_PERSONAL_TOKEN
            ).encode()
        },
    )
    assert response.status == 422
    assert await response.json() == {
        "detail": [
            {"loc": ["parameters", "owner"], "message": "'ab' is too short"}
        ]
    }


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
      """
      List all repositories in the repository.

      Args:
          aiohttp_client: (todo): write your description
          headers: (dict): write your description
      """
    client = await aiohttp_client(create_app())
    response = await client.get(URL_REPOSITORIES, headers=headers)

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
      """
      Test if a list of repositories.

      Args:
          aiohttp_client: (todo): write your description
          invalid_headers: (int): write your description
      """
    client = await aiohttp_client(create_app())
    response = await client.get(URL_REPOSITORIES, headers=invalid_headers)
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
      """
      Get a list of repositories existance.

      Args:
          aiohttp_client: (todo): write your description
          invalid_headers: (str): write your description
      """
    client = await aiohttp_client(create_app())
    response = await client.get(URL_REPOSITORIES, headers=invalid_headers)
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
      """
      Test for all repositories.

      Args:
          aiohttp_client: (todo): write your description
          invalid_headers: (str): write your description
      """
    client = await aiohttp_client(create_app())
    response = await client.get(URL_REPOSITORIES, headers=invalid_headers)
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
      """
      Retrieves the owner of an environment

      Args:
          aiohttp_client: (todo): write your description
      """
    client = await aiohttp_client(create_app())

    response = await client.get(
        URL_OWNER_REPOSITORIES_ENV,
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
      """
      Retrieves a repository.

      Args:
          aiohttp_client: (todo): write your description
      """
    client = await aiohttp_client(create_app())

    response = await client.get(
        URL_REPOSITORY,
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
      """
      Retrieves the repository of a valid.

      Args:
          aiohttp_client: (todo): write your description
          invalid_headers: (str): write your description
      """
    client = await aiohttp_client(create_app())

    response = await client.get(URL_REPOSITORY, headers=invalid_headers)
    assert response.status == 403
    assert await response.json() == {"detail": "Not authenticated"}


async def test_retrieve_repository_env_200(aiohttp_client):
      """
      Retrieves the environment configuration.

      Args:
          aiohttp_client: (todo): write your description
      """
    client = await aiohttp_client(create_app())

    response = await client.get(
        URL_REPOSITORY_ENV,
        headers={
            "X-GitHub-Username": GITHUB_USERNAME,
            "X-GitHub-Personal-Token": GITHUB_PERSONAL_TOKEN,
        },
    )
    assert response.status == 200
    assert await response.json() == {"LOCALE": "uk_UA.UTF-8"}
