"""
==============
rororo.openapi
==============

Cornerstone of *rororo* library, which brings OpenAPI 3 schema support for
aiohttp.web applications.

"""

from .contexts import openapi_context
from .exceptions import (
    BadRequest,
    BasicInvalidCredentials,
    BasicSecurityError,
    get_current_validation_error_loc,
    InvalidCredentials,
    ObjectDoesNotExist,
    SecurityError,
    ServerError,
    validation_error_context,
    ValidationError,
)
from .openapi import OperationTableDef, read_openapi_schema, setup_openapi
from .utils import (
    get_openapi_context,
    get_openapi_schema,
    get_openapi_spec,
    get_validated_data,
    get_validated_parameters,
)
from .views import default_error_handler


__all__ = (
    # contexts
    "openapi_context",
    # exceptions
    "BadRequest",
    "BasicInvalidCredentials",
    "BasicSecurityError",
    "get_current_validation_error_loc",
    "InvalidCredentials",
    "ObjectDoesNotExist",
    "SecurityError",
    "ServerError",
    "validation_error_context",
    "ValidationError",
    # openapi
    "OperationTableDef",
    "read_openapi_schema",
    "setup_openapi",
    # utils
    "get_openapi_context",
    "get_openapi_schema",
    "get_openapi_spec",
    "get_validated_data",
    "get_validated_parameters",
    # views
    "default_error_handler",
)
