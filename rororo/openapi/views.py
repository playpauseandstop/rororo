import yaml
from aiohttp import web

from .exceptions import ConfigurationError
from .utils import get_openapi_schema


async def openapi_schema(request: web.Request) -> web.Response:
    """Dump OpenAPI Schema into specified format."""
    schema_format = request.match_info.get("schema_format")
    schema = get_openapi_schema(request.app)

    if schema_format == "json":
        return web.json_response(schema)

    if schema_format == "yaml":
        return web.Response(
            text=yaml.dump(schema), content_type="application/yaml"
        )

    raise ConfigurationError(
        f"Schema format {schema_format} not supported at a moment."
    )
