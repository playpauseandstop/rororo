.. include:: ../README.rst

Installation
============

.. code-block:: bash

    pip install rororo

Or with `poetry <https://poetry.eustace.io/>`_:

.. code-block:: bash

    poetry add rororo

Quick Start
===========

.. code-block:: python

    import datetime
    from pathlib import Path

    import attr
    from aiohttp import web
    from rororo import get_openapi_request, RouteTableDef, setup_openapi


    # Step 1. Define Post dataclass
    @attr.dataclass
    class Post:
        title: str
        slug: str
        content: str
        tags: List[str] = attr.Factory(list)

        created_at: datetime.datetime = attr.Factory(datetime.datetime.utcnow)
        updated_at: datetime.datetime = attr.Factory(datetime.datestim.utcnow)


    # Step 2. Instantiate OpenAPI router
    routes = RouteTableDef(prefix="/api")


    # Step 3. Handler for OpenAPI operationId: ``add_post``
    @routes.post("/posts")
    async def add_post(request: web.Request) -> web.Response:
        # Read valid data and instantiate post dataclass
        post = Post(**get_openapi_request(request).data)

        # Add post to storage, like PostgreSQL database

        # Return post details as response
        return web.json_response(attr.asdict(post), status=201)


    # Step 4. Create the application and attach OpenAPI routes to it
    app = web.Application()
    app.router.add_routes(routes)

    # Step 5. Setup the schema to use from './openapi.yaml' file
    setup_openapi(app, Path(__file__).parent / 'openapi.yaml')

License
=======

*rororo* is licensed under the terms of `BSD-3-Clause License
<https://github.com/playpauseandstop/rororo/blob/LICENSE>`_.

Contents
========

.. toctree::
   :maxdepth: 3

   api
   changelog
