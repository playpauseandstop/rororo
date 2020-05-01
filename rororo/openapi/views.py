import logging

import yaml
from aiohttp import web
from aiohttp_middlewares import error_context

from .exceptions import ConfigurationError, OpenAPIError
from .utils import get_openapi_schema
from ..annotations import MappingStrStr


logger = logging.getLogger(__name__)


async def default_error_handler(request: web.Request) -> web.Response:
    """Default error handler which will ignore logging OpenAPI errors."""
    with error_context(request) as context:
        err = context.err
        headers: MappingStrStr = {}

        if isinstance(err, OpenAPIError):
            headers = err.headers
        else:
            logger.error(context.message, exc_info=True)

        return web.json_response(
            context.data, status=context.status, headers=headers,
        )


async def openapi_schema(request: web.Request) -> web.Response:
    """Dump OpenAPI Schema into specified format."""
    schema_format = request.match_info.get("schema_format")
    schema = get_openapi_schema(request.config_dict)

    if schema_format == "json":
        return web.json_response(schema)

    if schema_format == "yaml":
        safe_dumper = getattr(yaml, "CSafeDumper", yaml.SafeDumper)
        return web.Response(
            text=yaml.dump(schema, Dumper=safe_dumper),
            content_type="application/yaml",
        )

    raise ConfigurationError(
        f"Schema format {schema_format} not supported at a moment."
    )
