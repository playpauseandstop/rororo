======
rororo
======

.. image:: https://img.shields.io/circleci/project/github/playpauseandstop/rororo/master.svg
    :target: https://circleci.com/gh/playpauseandstop/rororo
    :alt: CircleCI

.. image:: https://img.shields.io/pypi/v/rororo.svg
    :target: https://pypi.org/project/rororo/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/pyversions/rororo.svg
    :target: https://pypi.org/project/rororo/
    :alt: Python versions

.. image:: https://img.shields.io/pypi/l/rororo.svg
    :target: https://github.com/playpauseandstop/rororo/blob/master/LICENSE
    :alt: BSD License

.. image:: https://coveralls.io/repos/playpauseandstop/rororo/badge.svg?branch=master&service=github
    :target: https://coveralls.io/github/playpauseandstop/rororo
    :alt: Coverage

.. image:: https://readthedocs.org/projects/rororo/badge/?version=latest
    :target: https://rororo.readthedocs.io/
    :alt: Documentation

`OpenAPI 3 <https://spec.openapis.org/oas/v3.0.2>`_ schema support
for `aiohttp.web <https://aiohttp.readthedocs.io/en/stable/web.html>`_
applications.

As well as bunch other utilities to build effective web applications with
Python 3 & ``aiohttp.web``.

* Works on Python 3.6+
* BSD licensed
* Source, issues, and pull requests `on GitHub
  <https://github.com/playpauseandstop/rororo>`_

Important
=========

**2.0.0** version still in development. To install it use,

.. code-block:: bash

    pip install rororo>=2.0.0a3

or,

.. code-block:: bash

    poetry add rororo^=2.0.0a3

Quick Start
===========

``rororo`` relies on valid OpenAPI schema file (both JSON or YAML formats
supported).

Example below, illustrates on how to handle operation ``hello_world`` from
`openapi.yaml <https://github.com/playpauseandstop/rororo/blob/feature-openapi/tests/openapi.yaml>`_
schema file.

.. code-block:: python

    from pathlib import Path
    from typing import List

    from aiohttp import web
    from rororo import openapi_context, OperationTableDef, setup_openapi


    operations = OperationTableDef()


    @operations.register
    async def hello_world(request: web.Request) -> web.Response:
        with openapi_context(request) as context:
            name = context.parameters.query.get("name", "world")
            return web.json_response({"message": f"Hello, {name}!"})


    def create_app(argv: List[str] = None) -> web.Application:
        app = web.Application()
        setup_openapi(
            app,
            Path(__file__).parent / "openapi.yaml",
            operations,
            route_prefix="/api"
        )
        return app

Check
`examples <https://github.com/playpauseandstop/rororo/tree/master/examples>`_
folder to see other examples on how to use OpenAPI 3 schemas with aiohttp.web
applications.
