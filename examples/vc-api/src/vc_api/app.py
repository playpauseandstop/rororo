from pathlib import Path
from typing import List, Union

from aiohttp import web
from vc_api.views import operations

from rororo import BaseSettings, setup_openapi, setup_settings


def create_app(
    argv: Union[List[str], None] = None,
    *,
    settings: Union[BaseSettings, None] = None,
) -> web.Application:
    if settings is None:
        settings = BaseSettings.from_environ()

    return setup_openapi(
        setup_settings(web.Application(), settings),
        Path(__file__).parent / "vc-api.yaml",
        operations,
        cache_create_schema_and_spec=True,
    )
