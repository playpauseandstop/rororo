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


__all__ = (
    "get_openapi_context",
    "get_openapi_schema",
    "get_openapi_spec",
    "openapi_context",
    "OperationTableDef",
    "setup_openapi",
)
