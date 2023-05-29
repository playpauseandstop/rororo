from pathlib import Path
from typing import List, Union

from aiohttp import web

from rororo import BaseSettings, setup_openapi, setup_settings
from vc_api.views import operations


def create_app(
    argv: Union[List[str], None] = None,
    *,
    settings: Union[BaseSettings, None] = None,
) -> web.Application:
    settings = settings or BaseSettings.from_environ()

    return setup_openapi(
        setup_settings(web.Application(), settings),
        Path(__file__).parent / "vc-api.yaml",
        operations,
        cache_create_schema_and_spec=settings.is_test,
    )
