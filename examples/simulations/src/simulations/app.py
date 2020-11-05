import copy
from pathlib import Path
from typing import List

import yaml
from aiohttp import web
from openapi_core.shortcuts import create_spec
from pyrsistent import thaw

from rororo import get_validated_data, OperationTableDef, setup_openapi
from rororo.openapi.openapi import get_default_yaml_loader
from .storage import DEFAULT_STORAGE


operations = OperationTableDef()


def create_app(argv: List[str] = None) -> web.Application:
    """
    Create a flask application.

    Args:
        argv: (list): write your description
    """
    schema = yaml.load(
        (Path(__file__).parent / "openapi.yaml").read_bytes(),
        Loader=get_default_yaml_loader(),
    )

    app = web.Application()
    app["storage"] = copy.deepcopy(DEFAULT_STORAGE)

    return setup_openapi(
        app,
        operations,
        schema=schema,
        spec=create_spec(schema),
    )


@operations.register
async def create_simulation(request: web.Request) -> web.Response:
      """
      Create a simulation.

      Args:
          request: (todo): write your description
          web: (todo): write your description
          Request: (todo): write your description
      """
    data = thaw(get_validated_data(request))
    request.app["storage"].append(data)
    return web.json_response(data, status=201)


@operations.register
async def list_simulations(request: web.Request) -> web.Response:
      """
      List all the list of all webulations.

      Args:
          request: (todo): write your description
          web: (todo): write your description
          Request: (todo): write your description
      """
    return web.json_response(request.app["storage"])
