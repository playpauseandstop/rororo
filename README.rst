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

Implement `aiohttp.web`_ `OpenAPI 3`_ server applications with schema first
approach.

As well as bunch other utilities to build effective server applications with
`Python`_ 3 & `aiohttp.web`_.

* Works on `Python`_ 3.6+
* Works with `aiohttp.web`_ 3.6+
* BSD licensed
* Source, issues, and pull requests `on GitHub
  <https://github.com/playpauseandstop/rororo>`_

.. _`OpenAPI 3`: https://spec.openapis.org/oas/v3.0.3
.. _`aiohttp.web`: https://aiohttp.readthedocs.io/en/stable/web.html
.. _`Python`: https://www.python.org/

Quick Start
===========

*rororo* relies on valid OpenAPI 3 schema file (both JSON or YAML formats
supported).

Example below, illustrates on how to handle operation ``hello_world`` from
`openapi.yaml </tests/openapi.yaml>`_ schema file.

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
        return setup_openapi(
            web.Application(),
            Path(__file__).parent / "openapi.yaml",
            operations,
            server_url="/api",
        )

Schema First Approach
---------------------

Unlike other popular Python OpenAPI 3 solutions, such as
`Django REST Framework`_, `FastAPI`_,  `flask-apispec`_, or `aiohttp-apispec`_
*rororo* **requires** you to provide valid `OpenAPI 3`_ schema first. This
makes *rororo* similar to `connexion`_, `pyramid_openapi3`_ and other schema
first libraries.

.. _`Django REST Framework`: https://www.django-rest-framework.org
.. _`FastAPI`: https://fastapi.tiangolo.com
.. _`flask-apispec`: https://flask-apispec.readthedocs.io
.. _`aiohttp-apispec`: https://aiohttp-apispec.readthedocs.io
.. _`connexion`: https://connexion.readthedocs.io
.. _`pyramid_openapi3`: https://github.com/Pylons/pyramid_openapi3

Class Based Views
-----------------

*rororo* supports `class based views <https://docs.aiohttp.org/en/stable/web_quickstart.html#aiohttp-web-class-based-views>`_
as well. `Todo-Backend </examples/todobackend>`_ example illustrates how to use
class based views for OpenAPI 3 servers.

In snippet below, *rororo* expects that OpenAPI 3 schema contains operation \
ID ``UserView.get``,

.. code-block:: python

    @operations.register
    class UserView(web.View):
        async def get(self) -> web.Response:
            ...

More Examples
-------------

Check `examples </examples>`_ folder to see other examples on how to build
aiohttp.web OpenAPI 3 server applications.
