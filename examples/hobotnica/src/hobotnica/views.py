import uuid

from aiohttp import web

from rororo import openapi_context, OperationTableDef
from rororo.openapi.exceptions import ObjectDoesNotExist
from .data import ENVIRONMENT_VARS, GITHUB_REPOSITORIES
from .decorators import login_required


operations = OperationTableDef()


@operations.register
@login_required
async def create_repository(request: web.Request) -> web.Response:
    with openapi_context(request) as context:
        return web.json_response(
            {
                **context.data,
                "uid": str(uuid.uuid4()),
                "jobs": ["test", "deploy"],
                "status": "cloning",
            },
            status=201,
        )


@operations.register
async def list_all_references(request: web.Request) -> web.Response:
    return web.json_response({"default_env": {"CI": "1", "HOBOTNICA": "1"}})


@operations.register
@login_required
async def list_favorites_repositories(request: web.Request) -> web.Response:
    with openapi_context(request) as context:
        return web.json_response(
            status=204, headers={"X-Order": context.parameters.query["order"]}
        )


@operations.register
@login_required
async def list_owner_repositories(request: web.Request) -> web.Response:
    with openapi_context(request) as context:
        username = context.security["basic"].login
        return web.json_response(
            list((GITHUB_REPOSITORIES.get(username) or {}).values())
        )


@operations.register
@login_required
async def list_repositories(request: web.Request) -> web.Response:
    with openapi_context(request) as context:
        username = context.parameters.header["X-GitHub-Username"]
        return web.json_response(
            list((GITHUB_REPOSITORIES.get(username) or {}).values())
        )


@operations.register
@login_required
async def retrieve_owner_env(request: web.Request) -> web.Response:
    with openapi_context(request) as context:
        owner = context.parameters.path["owner"]
        return web.json_response(ENVIRONMENT_VARS.get(owner) or {})


@operations.register
@login_required
async def retrieve_repository(request: web.Request) -> web.Response:
    with openapi_context(request) as context:
        owner = context.parameters.path["owner"]
        repository = (GITHUB_REPOSITORIES.get(owner) or {}).get(
            context.parameters.path["name"]
        )

        if not repository:
            raise ObjectDoesNotExist("Repository")

        return web.json_response(repository)


@operations.register
@login_required
async def retrieve_repository_env(request: web.Request) -> web.Response:
    with openapi_context(request) as context:
        owner = context.parameters.path["owner"]
        name = context.parameters.path["name"]
        env_key = f"{owner}/{name}"
        return web.json_response(ENVIRONMENT_VARS.get(env_key) or {})
