import uuid

from aiohttp import web

from rororo import openapi_context, OperationTableDef
from rororo.openapi.exceptions import ObjectDoesNotExist
from .data import GITHUB_REPOSITORIES
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
async def retrieve_repository(request: web.Request) -> web.Response:
    with openapi_context(request) as context:
        owner = context.parameters.path["owner"]
        repository = (GITHUB_REPOSITORIES.get(owner) or {}).get(
            context.parameters.path["name"]
        )

        if not repository:
            raise ObjectDoesNotExist("Repository")

        return web.json_response(repository)
