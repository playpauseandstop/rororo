"""
==============
rororo.openapi
==============

Cornerstone of ``rororo`` library, which brings OpenAPI 3 schema support for
aiohttp.web applications.

"""

from .contexts import openapi_context
from .openapi import OperationTableDef, setup_openapi
from .utils import get_openapi_context, get_openapi_schema, get_openapi_spec
from .views import default_error_handler


__all__ = (
    "default_error_handler",
    "get_openapi_context",
    "get_openapi_schema",
    "get_openapi_spec",
    "openapi_context",
    "OperationTableDef",
    "setup_openapi",
)
