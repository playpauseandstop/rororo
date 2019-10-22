import types
from typing import Optional, Union

from aiohttp import BasicAuth, hdrs, web

from .constants import OPENAPI_SECURITY_API_KEY, OPENAPI_SECURITY_HTTP
from .data import OpenAPIOperation
from .exceptions import SecurityError
from ..annotations import DictStrAny, MappingStrAny


AUTHORIZATION_HEADER = hdrs.AUTHORIZATION
BEARER = "Bearer"


def get_security_data(
    request: web.Request, item: str, *, oas: DictStrAny
) -> Optional[Union[str, BasicAuth]]:
    """Get security data from request.

    Currently supported getting API Key & HTTP security data. OAuth & OpenID
    data not supported yet.
    """
    schema = oas["components"]["securitySchemes"].get(item)
    if not schema:
        return None

    security_type = schema["type"]
    if security_type == OPENAPI_SECURITY_API_KEY:
        location = schema["in"]
        name = schema["name"]

        # API Key from query string
        if location == "query":
            return request.rel_url.query.get(name)
        # API Key from headers
        if location == "header":
            return request.headers.get(name)
        # API Key from cookies
        if location == "cookie":
            return request.cookies.get(name)
    elif security_type == OPENAPI_SECURITY_HTTP:
        authorization_header = request.headers.get(AUTHORIZATION_HEADER)
        scheme = schema["scheme"]

        # Basic HTTP authentication
        if scheme == "basic":
            try:
                return BasicAuth.decode(auth_header=authorization_header)
            except ValueError:
                return None

        # Bearer authorization (JWT)
        if scheme == "bearer":
            stop = len(BEARER) + 1
            if (
                not authorization_header
                or authorization_header[:stop].lower() != "bearer "
            ):
                return None

            return authorization_header[stop:]

    return None


def validate_security(
    request: web.Request, operation: OpenAPIOperation, *, oas: DictStrAny
) -> MappingStrAny:
    """Validate security data for the request if any.

    First, check whether operation is secured or there is global security
    definitions. If not and current operation is not secured - return empty
    :class:`types.MappingProxyType`.

    If operation secured, go through all security items and attempt to match
    their data in request. If some of security items is matched - return it
    as result, if not - raise `SecurityError`.
    """
    security_list = operation.schema.get("security") or oas.get("security")
    if not security_list:
        return types.MappingProxyType({})

    for item in security_list:
        data = {key: get_security_data(request, key, oas=oas) for key in item}
        if all(value for value in data.values()):
            return types.MappingProxyType(data)

    raise SecurityError(
        "Operation is not secured, but should be due to OpenAPI Schema "
        "definition."
    )
