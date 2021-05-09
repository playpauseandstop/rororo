from functools import wraps

from aiohttp import web

from rororo import openapi_context
from rororo.annotations import Handler

from .auth import authenticate


def login_required(handler: Handler) -> Handler:
    @wraps(handler)
    async def decorator(request: web.Request) -> web.StreamResponse:
        with openapi_context(request) as context:
            basic_auth = context.security.get("basic")
            if basic_auth is not None:
                username = basic_auth.login
                personal_token = basic_auth.password
            else:
                username = context.parameters.header["X-GitHub-Username"]
                personal_token = (
                    context.security.get("personalToken")
                    or context.security["jwt"]
                )

            authenticate(username=username, personal_token=personal_token)

        return await handler(request)

    return decorator
