"""
======
rororo
======

`OpenAPI 3 <https://spec.openapis.org/oas/v3.0.2>`_ schema support
for `aiohttp.web <https://aiohttp.readthedocs.io/en/stable/web.html>`_
applications.

As well as bunch other utilities to build effective web applications with
Python 3 & ``aiohttp.web``.

"""

from .openapi import (
    get_openapi_context,
    get_openapi_schema,
    get_openapi_spec,
    openapi_context,
    OperationTableDef,
    setup_openapi,
)
from .settings import BaseSettings, env_factory, setup_settings


__all__ = (
    "BaseSettings",
    "env_factory",
    "get_openapi_context",
    "get_openapi_schema",
    "get_openapi_spec",
    "openapi_context",
    "OperationTableDef",
    "setup_openapi",
    "setup_settings",
)

__author__ = "Igor Davydenko"
__license__ = "BSD-3-Clause"
__version__ = "2.0.0b3"
