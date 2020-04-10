=======================
Handling OpenAPI Errors
=======================

By default, :func:`rororo.openapi.setup_openapi` enables usage of
:func:`aiohttp_middlewares.error.error_middleware`, which in same time provides
human readable JSON errors for:

- Security error
- Request parameter validation error
- Request body validation error
- Response data validation error

Document below describes how exactly those errors handled, and what changes
to OpenAPI Schema you might add to support given error responses.

Security Errors
===============

OpenAPI 3 schema provide a way to "secure" operation via
`security schemes <https://swagger.io/docs/specification/authentication/>`_. As
of rororo **2.0.0** version next security schemes are supported:

- HTTP

  - Basic
  - Bearer

- API Key

**Unfortunately OpenID & OAuth 2 security schemas not yet supported.**

Under the hood rororo uses next logic for generating security error,

- When an operation is guarded with one and only security scheme of HTTP Basic
  authentication and ``Authorization`` header is missed or contains wrong data -
  `401 Unauthenticated` error raised
- If an operation guarded with other security scheme or with multiple security
  schemes and security data is missed in request - `403 Access Denied` error
  raised

Both of given errors results in next JSON:

.. code-block:: json

    {
        "detail": "Not authenticated"
    }

Only difference is response status code & additional ``www-authenticate: basic``
header in case of missing HTTP Basic Auth details.

.. important::
    ``rororo`` does not intend to check, whether authentication data is valid
    or not, so ``aiohttp.web`` application should make the authentication by
    itself. Most reliable way of doing that by providing ``@login_required``
    decorator as `done in Hobotnica example <https://github.com/playpauseandstop/rororo/blob/master/examples/hobotnica/decorators.py>`_.

Request Parameter Validation Errors
===================================

When request parameter is missed, when required, missed, has empty, or invalid
value `openapi-core <https://pypi.org/project/openapi-core/>`_ raises an
``OpenAPIParameterError`` or ``EmptyParameterValue`` exception. ``rororo``
handles given error and wraps it into own ``ValidationError``.

For example, when operation is required ``X-GitHub-Username`` header parameter,
missing it in request will result in ``422 Unprocessable Entity`` response
with next JSON content:

.. code-block:: json

    {
        "detail": [
            {
                "loc": [
                    "parameters",
                    "X-GitHub-Username"
                ],
                "message": "Required parameter"
            }
        ]
    }

Request Body Validation Errors
==============================

When request body contains invalid data ``rororo`` converts any
``openapi-core`` or ``jsonschema`` exceptions into own ``ValidationError``.

For example, when request body missed ``name`` field and have invalid ``email``
field next response will be supplied:

.. code-block:: json

    {
        "detail": [
            {
                "loc": [
                    "body",
                    "name"
                ],
                "message": "Field required"
            },
            {
                "loc": [
                    "body",
                    "email"
                ],
                "message": "'not-email' is not an 'email'"
            }
        ]
    }

Response Data Validation Errors
===============================

Similarly to `Request Body Validation Errors`_ ``rororo`` converts any
``openapi-core`` or ``jsonschema`` exceptions raised by validating response
data into own ``ValidationError``.

.. important::

    For performance reasons, you might want to disable response data validation
    entirely by passing ``is_validate_response=False`` into
    :func:`rororo.openapi.setup_openapi`. In that case ``rororo`` will not
    run any validation for response data.

For example, when response data contains wrong ``uid`` format field next error
response will be supplied,

.. code-block:: json

    {
        "detail": [
            {
                "loc": [
                    "response",
                    "uid"
                ],
                "message": "'not-uid' is not a 'uuid'"
            }
        ]
    }

OpenAPI Schemas
===============

You might need to update your OpenAPI 3 Schemas by using next responses
components.

Default Error
-------------

.. code-block:: yaml

    components:
      responses:
        DefaultError:
          description: "Unhandled error."
          content:
            application/json:
              schema:
                type: "object"
                properties:
                  detail:
                    type: "string"
                    minLength: 1
                required: ["detail"]

Validation Error
----------------

.. code-block:: yaml

    components:
      responses:
        ValidationError:
          description: "Validation error."
          content:
            application/json:
              schema:
                type: "object"
                properties:
                  detail:
                    type: "array"
                    items:
                      type: "object"
                      properties:
                        loc:
                          type: "array"
                          items:
                            type: "string"
                            minLength: 1
                        message:
                          type: "string"
                          minLength: 1
                      required: ["loc", "message"]
                required: ["detail"]

Custom Error Handling
=====================

In case if ``aiohttp.web`` application doesn't want or cannot use described way
of handling errors via :func:`aiohttp_middlewares.error.error_middleware`, it
needs to disable error middleware usage entirely by passing
``use_error_middleware=False`` on setting up OpenAPI support,

.. code-block:: python

    from pathlib import Path

    from aiohttp import web
    from rororo import setup_openapi


    app = setup_openapi(
        web.Application(),
        Path(__file__).parent / "openapi.yaml",
        operations,
        use_error_middleware=False,
    )

In that case ``aiohttp.web`` application need to implement its own way of
handling OpenAPI (and other) errors.
