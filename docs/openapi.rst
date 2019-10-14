============================================
OpenAPI Support for aiohttp.web applications
============================================

`OpenAPI 3 <https://spec.openapis.org/oas/v3.0.2>`_ is a powerful way of
describing request / response specifications for API endpoints. There are
two ways on supporting OpenAPI 3 for Python web applications:

- Generate the schema from Python data structures (as done in
  `django-rest-framework <https://www.django-rest-framework.org/>`_,
  `fastapi <https://fastapi.tiangolo.com>`_,
  `aiohttp-apispec <https://aiohttp-apispec.readthedocs.io>`_ and others)
- Rely on OpenAPI 3 schema file (as done in
  `pyramid_openapi3 <https://github.com/Pylons/pyramid_openapi3>`_)

While both ways has their pros & cons, `rororo` library is heavily inspired by
`pyramid_openapi3 <https://github.com/Pylons/pyramid_openapi3>`_ and as result
**requires valid** OpenAPI 3 schema file to be provided.

In total OpenAPI 3 schema support fo ``aiohttp.web`` applications done in 3
parts:

1. Provide **valid** OpenAPI 3 schema file
2. Map ``operationId`` with ``aiohttp.web`` view handler via
   :class:`rororo.openapi.OperationTableDef`
3. Call :func:`rororo.openapi.setup_openapi` to finish setup process

Below more details provided for all of significant parts.

Part 1. Provide OpenAPI 3 schema file
=====================================

From one point of view, generating OpenAPI 3 schemas from Python data
structures is more *Pythonic* way, but it results in several issues:

- Which Python data structure use as a basis? For example,

  - `django-rest-framework`_ generates OpenAPI 3 schemas from their own
    serializers
  - `fastapi`_ relies on `pydantic <https://pydantic-docs.helpmanual.io>`_
    models
  - While `aiohttp-apispec`_ built on top of
    `apispec <https://apispec.readthedocs.io>`_ library, which behind the
    scenes utilies `marshmallow <https://marshmallow.readthedocs.io/>`_ data
    structures

- Data structure library need to support whole OpenAPI 3 specification on their
  own
- Sharing OpenAPI 3 schema with other parts of your application (frontend,
  mobile application, etc) became a tricky task, *which in most cases requires
  to be handled by specific CI/CD job*

In same time, as *rororo* requires OpenAPI 3 schema file it allows to,

- Use any Python data structure library for accessing valid request data and
  for providing valid response data
- Track changes to OpenAPI specification file directly with source control
  management system as *git* or *mercurial*
- Use all available OpenAPI 3 specification features

To start with OpenAPI 3 schema it is recommended to,

- Check whole `OpenAPI 3`_ specification
- Read `OpenAPI 3 Documentation <https://swagger.io/docs/specification/about/>`_
- Browse through `OpenAPI 3 Examples <https://github.com/OAI/OpenAPI-Specification/tree/master/examples/v3.0>`_
- Try `Swagger Editor <https://editor.swagger.io>`_ online tool

Part 2. Map operation with view handler
=======================================

After OpenAPI 3 schema file is valid and ready to be used, it is needed to
map `OpenAPI operations <https://spec.openapis.org/oas/v3.0.2#operation-object>`_
with `aiohttp.web view handlers <https://aiohttp.readthedocs.io/en/stable/web_quickstart.html#handler>`_.

As *operationId* field for the operation is,

    Unique string used to identify the operation. The id MUST be unique among
    all operations described in the API.

It is a possibility to tell ``aiohttp.web`` to use specific view as a handler
for given OpenAPI 3 operation.

For example,

1. OpenAPI 3 specification contains ``hello_world`` operation
2. ``api.views`` module contains ``hello_world`` view handler

To connect both of described parts :class:`rororo.openapi.OperationTableDef`
need to be used as (in ``views.py``):

.. code-block:: python

    from aiohttp import web
    from rororo import OperationTableDef


    operations = OperationTableDef()


    @operations.register
    async def hello_world(request: web.Request) -> web.Response:
        return web.json_response("Hello, world!")

In case, when *operationId* does not match with view handler name it is safe
to pass ``operation_id`` string as first argument to ``@operations.register``,

.. code-block:: python

    @operations.register("hello_world")
    async def not_a_hello_world(request: web.Request) -> web.Response:
        return web.json_response("Hello, world!")

Request Validation
------------------

Decorating view handler with ``@operations.register`` will ensure that it will
be executed only with valid request body & parameters according to OpenAPI 3
operation specification.

If any parameters are missed or invalid, as well as if request body does not
pass validation it will result in 422 response.

Accessing Valid Request Data
----------------------------

To access valid data for given request it is recommended to use
:func:`rororo.openapi.openapi_context` context manager as follows,

.. code-block:: python

    @operations.register
    async def add_pet(request: web.Request) -> web.Response:
        with openapi_context(request) as context:
            ...

Resulted *context* instance will contain,

- ``request`` - untouched :class:`aiohttp.web.Request` instance
- ``app`` - :class:`aiohttp.web.Application` instance
- ``config_dict``
- ``operation`` - operation details (``id``, ``schema``, etc)
- ``parameters`` - valid parameters mappings (``path``, ``query``, ``header``,
  ``cookie``)
- ``data`` - valid data from request body
- ``security`` - security data, if operation is secured

Part 3. Finish setup process
============================

After the OpenAPI 3 schema is provided and view handlers is mapped to OpenAPI
operations it is a time to tell an :class:`aiohttp.web.Application` to use
given schema file and operations mapping(s) via
:func:`rororo.openapi.setup_openapi`.

In most cases this setup should be done in application factory function as
follows,

.. code-block:: python

    from pathlib import Path
    from typing import List

    from aiohttp import web
    from rororo import setup_openapi

    from .views import operations


    OPENAPI_YAML_PATH = Path(__file__).parent / "openapi.yaml"


    def create_app(argv: List[str] = None) -> web.Application:
        app = web.Application()
        setup_openapi(app, OPENAPI_YAML_PATH, opeartions)
        return app

.. important::
    By default, due to performance considerations, *rororo* will not enable
    response validation. But to ensure, that all views result valid responses
    according to OpenAPI 3 schema, pass ``is_validate_response`` truthy flag to
    :func:`rororo.openapi.setup_openapi`

.. note::
    It is recommended to store OpenAPI 3 schema file next to main application
    module, which semantically will mean: this is an OpenAPI 3 schema file for
    current application.

    But it is not mandatory, and you might want to specify any accessible file
    path, you want.

.. note::
    By default, OpenAPI schema, which is used for the application will be
    available via GET requests to ``{route_prefix}/openapi.(json|yaml)``, but
    it is possible to not serve the schema by passing
    ``has_openapi_schema_handler`` falsy flag to
    :func:`rororo.openapi.setup_openapi`

Configuration & Operation Errors
--------------------------------

Setting up OpenAPI for aiohttp.web applicaitons via
:func:`rororo.openapi.setup_openapi` may result in numerous errors as it relies
on many things. While most of the errors designed to be self-descriptive below
more information added about most possible cases.

OpenAPI 3 Schema file does not exist or not readable
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*rororo* expects that ``schema_path`` is a path to a readable file with
OpenAPI schema. To fix the error, pass proper path.

Unable to read OpenAPI 3 Schema from the file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*rororo* supports reading OpenAPI 3 schema from JSON & YAML files with
extensions: ``.json``, ``.yml``, ``.yaml``. If the ``schema_path`` file
contains valid OpenAPI 3 schema, but has different extension, consider rename
it. Also, in same time *rororo* expects that ``.json`` files contain valid
JSON, while ``.yml`` / ``.yaml`` files contain valid YAML data.

OpenAPI 3 Schema is not valid
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*rororo* **requires** your OpenAPI 3 schema file to be a valid one. If the file
is not valid consider running
`openapi-spec-validator <https://pypi.org/project/openapi-spec-validator>`_
against your file to find the issues.

.. note::
    *rororo* depends on *openapi-spec-validator* (via *openapi-core*), which
    means after installing *rororo*, virtual environment (or system) will
    have ``openapi-spec-validator`` script available

Operation not found
~~~~~~~~~~~~~~~~~~~

Please, use valid *operationId* while mapping OpenAPI operation to aiohttp.web
view handler.

Using invalid *operationId* will result in runtime error, which doesn't allow
aiohttp.web application to start up.

Accessing OpenAPI Schema & Spec
-------------------------------

After OpenAPI setting up for :class:`aiohttp.web.Application` it is possible
to access OpenAPI Schema & Spec inside of any view handler as follows,

.. code-block::

    from rororo import get_openapi_schema, get_openapi_spec


    async def something(request: web.Request) -> web.Response:
        # `Dict[str, Any]` with OpenAPI schema
        schema = get_openapi_schema(request.app)

        # `openapi_core.schemas.specs.models.Spec` instance
        spec = get_openapi_spec(request.config_dict)

        ...

How it Works?
=============

Under the hood *rororo* heavily uses
`openapi-core <https://pypi.org/project/openapi-core>`_ library.

1. :func:`rororo.openapi.setup_openapi` creates the spec instance
2. On handling each request ``validate_parameters`` / ``validate_body``
   shortcut functions called
3. If enabled, ``validate_data`` shortcut called for each response

Swagger 2.0 Support
===================

While *rororo* designed to support **only** OpenAPI 3 Schemas due to
`openapi-core`_ dependency it is technically able to support Swagger 2.0 for
aiohttp.web applications in same  manner as well.

.. important::
    Swagger 2.0 support is not tested at all and *rororo* is not intended to
    provide it.

    With that in mind please consider *rororo* only as a library to bring
    **OpenAPI 3 Schemas** support for ``aiohttp.web`` applications.
