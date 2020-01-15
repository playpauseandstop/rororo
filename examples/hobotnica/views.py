import logging

from aiohttp import web

from rororo import openapi_context, OperationTableDef
from .data import GITHUB_REPOSITORIES
from .decorators import login_required
from .exceptions import ObjectDoesNotExist


logger = logging.getLogger(__name__)
operations = OperationTableDef()


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
