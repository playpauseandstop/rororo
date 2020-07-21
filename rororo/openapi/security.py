from typing import cast, Optional, Union

from aiohttp import BasicAuth, hdrs
from openapi_core.schema.operations.models import Operation
from openapi_core.schema.security_schemes.enums import (
    HttpAuthScheme,
    SecuritySchemeType,
)
from openapi_core.schema.security_schemes.models import SecurityScheme
from openapi_core.security.exceptions import SecurityError as CoreSecurityError
from openapi_core.validation.request.datatypes import OpenAPIRequest
from openapi_core.validation.request.validators import RequestValidator
from pyrsistent import pmap

from .exceptions import BasicSecurityError, SecurityError
from ..annotations import MappingStrAny


AUTHORIZATION_HEADER = hdrs.AUTHORIZATION


def basic_auth_factory(value: str) -> BasicAuth:
    # Workaround for ``openapi-core==0.13.3``
    if ":" in value:
        return BasicAuth(*(item.strip() for item in value.split(":", 1)))
    # In ``openapi-core==0.13.4`` parsing security schemas changed, now the
    # value for basic auth is base64 encoded string
    return BasicAuth.decode(f"Basic {value}")


def get_jwt_security_data(request: OpenAPIRequest) -> Optional[str]:
    """Get JWT bearer security data.

    At a moment, openapi-core attempts to decode JWT header using same rules
    as for basic auth, which might return unexpected results.
    """
    header: Optional[str] = request.parameters.header.get(AUTHORIZATION_HEADER)

    # Header does not exist
    if header is None:
        return None

    try:
        maybe_bearer, value = header.split(" ", 1)
    except ValueError:
        return None

    if maybe_bearer.lower() != "bearer":
        return None

    return value


def get_security_data(
    validator: RequestValidator, request: OpenAPIRequest, scheme_name: str
) -> Optional[Union[BasicAuth, str]]:
    """Get security data from request.

    Currently supported getting API Key & HTTP security data. OAuth & OpenID
    data not supported yet.
    """
    if is_jwt_bearer_security_scheme(validator, scheme_name):
        return get_jwt_security_data(request)

    try:
        value: str = validator._get_security_value(scheme_name, request)
    except CoreSecurityError:
        return None

    if is_basic_auth_security_scheme(validator, scheme_name):
        return basic_auth_factory(value)
    return value


def get_security_scheme(
    validator: RequestValidator, scheme_name: str
) -> Optional[SecurityScheme]:
    return validator.spec.components.security_schemes.get(scheme_name)


def is_basic_auth_security_scheme(
    validator: RequestValidator, scheme_name: str
) -> bool:
    scheme = get_security_scheme(validator, scheme_name)
    if scheme is None:
        return False
    return cast(
        bool,
        scheme.type == SecuritySchemeType.HTTP
        and scheme.scheme == HttpAuthScheme.BASIC,
    )


def is_jwt_bearer_security_scheme(
    validator: RequestValidator, scheme_name: str
) -> bool:
    scheme = get_security_scheme(validator, scheme_name)
    if scheme is None:
        return False
    return cast(
        bool,
        scheme.type == SecuritySchemeType.HTTP
        and scheme.scheme == HttpAuthScheme.BEARER,
    )


def validate_security(
    validator: RequestValidator, request: OpenAPIRequest, operation: Operation
) -> MappingStrAny:
    """Validate security data for the request if any.

    First, check whether operation is secured or there is global security
    definitions. If not and current operation is not secured - return empty
    :class:`pyrsistent.PMap`.

    If operation secured, go through all security items and attempt to match
    their data in request. If some of security items is matched - return it
    as result, if not - raise `SecurityError`.
    """
    security_list = operation.security or validator.spec.security
    if not security_list:
        return pmap()

    # If operation "secured" with an empty object it means the whole security
    # rules are optional. However to not return empty security details it is
    # needed to move given security scheme to the bottom
    has_empty_security = {} in security_list
    if has_empty_security:
        security_list.remove({})
        security_list.append({})

    for item in security_list:
        data = {
            key: get_security_data(validator, request, key) for key in item
        }
        if all(value for value in data.values()):
            return pmap(data)

    # To supply proper security error need to check how many security schemas
    # should be applied for given operation
    #
    # If there is only one security schema with one security schema item and
    # it is a HTTP basic - raise BasicSecurityError (401 Unauthenticated). In
    # all other cases - raise a SecurityError (403 Access Denied)
    if len(security_list) == 1 and len(security_list[0]) == 1:
        scheme_name = list(security_list[0].keys())[0]
        if is_basic_auth_security_scheme(validator, scheme_name):
            raise BasicSecurityError()

    raise SecurityError()
