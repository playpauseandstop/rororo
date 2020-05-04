======
rororo
======

.. image:: https://github.com/playpauseandstop/rororo/workflows/ci/badge.svg
    :target: https://github.com/playpauseandstop/rororo/actions?query=workflow%3A%22ci%22
    :alt: CI Workflow

.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
    :target: https://github.com/pre-commit/pre-commit
    :alt: pre-commit

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: black

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

    pip install rororo==2.0.0rc1

or,

.. code-block:: bash

    poetry add rororo==2.0.0rc1

Quick Start
===========

``rororo`` relies on valid OpenAPI schema file (both JSON or YAML formats
supported).

Example below, illustrates on how to handle operation ``hello_world`` from
`openapi.yaml <https://github.com/playpauseandstop/rororo/blob/master/tests/openapi.yaml>`_
schema file.

.. code-block:: python

    from pathlib import Path
    from typing import List

    from aiohttp import web
    from rororo import (
        openapi_context,
        OperationTableDef,
        setup_openapi,
    )


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
            route_prefix="/api",
        )
        return app

Class Based Views
-----------------

``rororo`` supports `class based views <https://docs.aiohttp.org/en/stable/web_quickstart.html#aiohttp-web-class-based-views>`_
as well. `Todo-Backend <https://github.com/playpauseandstop/rororo/tree/master/examples/todobackend>`_
example illustrates how to use class based views for OpenAPI handlers.

In snippet below, ``rororo`` expects that OpenAPI schema contains operation ID
``UserView.get``,

.. code-block:: python

    @operations.register
    class UserView(web.View):
        async def get(self) -> web.Response:
            ...

More Examples
-------------

Check
`examples <https://github.com/playpauseandstop/rororo/tree/master/examples>`_
folder to see other examples on how to use OpenAPI 3 schemas with aiohttp.web
applications.
