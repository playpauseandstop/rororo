======================================================
aiohttp.web OpenAPI 3 schema first server applications
======================================================

`OpenAPI 3 <https://spec.openapis.org/oas/v3.0.3>`_ is a powerful way of
describing request / response specifications for API endpoints. There are
two ways on using OpenAPI 3 within Python server applications:

- Generate the schema from Python data structures (as done in
  `Django REST Framework <https://www.django-rest-framework.org/>`_,
  `FastAPI <https://fastapi.tiangolo.com>`_,
  `aiohttp-apispec <https://aiohttp-apispec.readthedocs.io>`_ and others)
- Rely on OpenAPI 3 schema file (as done in
  `pyramid_openapi3 <https://github.com/Pylons/pyramid_openapi3>`_)

While both ways have their pros & cons, `rororo` library is heavily inspired by
`pyramid_openapi3 <https://github.com/Pylons/pyramid_openapi3>`_ and as result
**requires valid** OpenAPI 3 schema file to be provided.

In total, to build aiohttp.web OpenAPI 3 server applications with *rororo*
you need to:

1. Provide **valid** OpenAPI 3 schema file
2. Map ``operationId`` with ``aiohttp.web`` view handler via
   :class:`rororo.openapi.OperationTableDef`
3. Call :func:`rororo.openapi.setup_openapi` to finish setup process

Below more details provided for all significant parts.

Part 1. Provide OpenAPI 3 schema file
=====================================

From one point of view, generating OpenAPI 3 schemas from Python data
structures is more *Pythonic* way, but it results in several issues:

- Which Python data structure use as a basis? For example,

  - `Django REST Framework`_ generates OpenAPI 3 schemas from their own
    serializers
  - `FastAPI`_ relies on `pydantic <https://pydantic-docs.helpmanual.io>`_
    models
  - While `aiohttp-apispec`_ built on top of
    `APISpec <https://apispec.readthedocs.io>`_ library, which behind the
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
map `OpenAPI operations <https://spec.openapis.org/oas/v3.0.3#operation-object>`_
with `aiohttp.web view handlers <https://aiohttp.readthedocs.io/en/stable/web_quickstart.html#handler>`_.

As *operationId* field for the operation is,

    Unique string used to identify the operation. The id MUST be unique among
    all operations described in the API.

It makes possible to tell ``aiohttp.web`` to use specific view as a handler
for every given OpenAPI 3 operation.

For example,

1. OpenAPI 3 specification has ``hello_world`` operation
2. ``api.views`` module has ``hello_world`` view handler

To connect both of described parts :class:`rororo.openapi.OperationTableDef`
need to be used as (in ``views.py``):

.. code-block:: python

    from aiohttp import web
    from rororo import OperationTableDef


    operations = OperationTableDef()


    @operations.register
    async def hello_world(request: web.Request) -> web.Response:
        return web.json_response("Hello, world!")

In case, when *operationId* does not match view handler name it is needed to
to pass ``operation_id`` string as first argument of ``@operations.register``
decorator,

.. code-block:: python

    @operations.register("hello_world")
    async def not_a_hello_world(
        request: web.Request,
    ) -> web.Response:
        return web.json_response("Hello, world!")

Class Based Views
-----------------

*rororo* supports `class based views <https://docs.aiohttp.org/en/stable/web_quickstart.html#aiohttp-web-class-based-views>`_
as well.

In basic mode it expects that OpenAPI schema contains *operationId*, which
equals to all view method qualified names. For example, code below expects
OpenAPI schema to declare ``UsersView.get`` & ``UsersView.post`` operation IDs,

.. code-block:: python

    @operations.register
    class UsersView(web.View):
        async def get(self) -> web.Response:
            ...

        async def post(self) -> web.Response:
            ...

Next, it might be useful to provide different prefix instead of ``UsersView``.
In example below, *rororo* expects OpenAPI schema to provide ``users.get`` &
``users.post`` operation IDs,

.. code-block:: python

    @operations.register("users")
    class UsersView(web.View):
        async def get(self) -> web.Response:
            ...

        async def post(self) -> web.Response:
            ...

Finally, it might be useful to provide custom *operationId* instead of guessing
it from view or view method name. Example below, illustrates the case, when
OpenAPI schema contains ``list_users`` & ``create_user`` operation IDs,

.. code-block:: python

    @operations.register
    class UsersView(web.View):
        @operations.register("list_users")
        async def get(self) -> web.Response:
            ...

        @operations.register("create_user")
        async def post(self) -> web.Response:
            ...

To access :class:`rororo.openapi.data.OpenAPIContext` in class based views you
need to pass ``self.request`` into :func:`rororo.openapi.openapi_context` or
:func:`rororo.openapi.get_openapi_context` as done below,

.. code-block:: python

    @operations.register
    class UserView(web.View):
        async def patch(self) -> web.Response:
            user = get_user_or_404(self.request)
            with openapi_context(self.request) as context:
                next_user = attr.evolve(user, **context.data)
                save_user(next_user)
            return web.json_response(next_user.to_api_dict())

.. important::
    On registering class based views with multiple view methods (for example
    with ``get``, ``patch`` & ``put``) you need to ensure that **all** methods
    could be mapped to operation ID in provided OpenAPI schema file.

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
- ``parameters`` - valid parameters mappings (``path``, ``query``, ``header``,
  ``cookie``)
- ``security`` - security data, if operation is secured
- ``data`` - valid data from request body

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

.. note::
    It is recommended to store OpenAPI 3 schema file next to main application
    module, which semantically will mean: this is an OpenAPI 3 schema file for
    current application.

    But it is not mandatory, and you might want to specify any accessible file
    path, you want.

.. note::
    By default, OpenAPI schema, which is used for the application will be
    available via GET requests to ``{server_url}/openapi.(json|yaml)``, but
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

Under the hood *rororo* heavily relies on
`openapi-core <https://pypi.org/project/openapi-core>`_ library.

1. :func:`rororo.openapi.setup_openapi`

   - Creates the `Spec <https://github.com/p1c2u/openapi-core/blob/0.13.3/openapi_core/schema/specs/models.py#L14>`_
     instance from OpenAPI schema source
   - Connects previously registered handlers and views to the application router
     (:class:`aiohttp.web.UrlDispatcher`)
   - Registers hidden ``openapi_middleware`` to handle request to registered
     handlers and views

2. On handling each OpenAPI request `RequestValidator.validate(...) <https://github.com/p1c2u/openapi-core/blob/0.13.3/openapi_core/validation/request/validators.py#L27>`_
   method called. Result of validation as
   :class:`rororo.openapi.data.OpenAPIContext` supplied to current
   :class:`aiohttp.web.Request` instance
3. If enabled, `ResponseValidator.validate(...) <https://github.com/p1c2u/openapi-core/blob/0.13.3/openapi_core/validation/response/validators.py#L19>`_
   method called for each OpenAPI response

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
