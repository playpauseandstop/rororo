import types
from typing import Optional, Union

from aiohttp import BasicAuth, hdrs, web

from .constants import OPENAPI_SECURITY_API_KEY, OPENAPI_SECURITY_HTTP
from .data import OpenAPIOperation
from .exceptions import BasicSecurityError, SecurityError
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
            return request.rel_url.query.get(name)  # type: ignore
        # API Key from headers
        if location == "header":
            return request.headers.get(name)  # type: ignore
        # API Key from cookies
        if location == "cookie":
            return request.cookies.get(name)  # type: ignore
    elif security_type == OPENAPI_SECURITY_HTTP:
        authorization_header = request.headers.get(AUTHORIZATION_HEADER)
        scheme = schema["scheme"]

        # Basic HTTP authentication
        if scheme == "basic":
            try:
                return BasicAuth.decode(auth_header=authorization_header)
            except (AttributeError, ValueError):
                return None

        # Bearer authorization (JWT)
        if scheme == "bearer":
            stop = len(BEARER) + 1
            if (
                not authorization_header
                or authorization_header[:stop].lower() != "bearer "
            ):
                return None

            return authorization_header[stop:]  # type: ignore

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

    # To supply proper security error need to check how many security schemas
    # should be applied for given operation
    #
    # If there is only one security schema with one security schema item and
    # it is a HTTP basic - raise BasicSecurityError (401 Unauthenticated). In
    # all other cases - raise a SecurityError (403 Access Denied)
    if len(security_list) == 1 and len(security_list[0]) == 1:
        security_key = list(security_list[0].keys())[0]
        schema = oas["components"]["securitySchemes"].get(security_key)

        if (
            schema["type"] == OPENAPI_SECURITY_HTTP
            and schema["scheme"] == "basic"
        ):
            raise BasicSecurityError()

    raise SecurityError()
