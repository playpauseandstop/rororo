==================================
Known OpenAPI limitations & issues
==================================

There are some limitations & issues in providing OpenAPI 3 support for
aiohttp.web applications via ``rororo`` library.

.. important::
    In case, if your issue not listed below, feel free to open
    `new issue <https://github.com/playpauseandstop/rororo/issues/new>`_ at
    Github.

Limitations
===========

Unsupported Security Schemes
----------------------------

As of ``2.0.0rc0`` release
`OAuth2 <https://swagger.io/docs/specification/authentication/oauth2/>`_ &
`OpenID <https://swagger.io/docs/specification/authentication/openid-connect-discovery/>`_
security schemes is not supported. And at a moment there is no plans of adding
support of given security schemes to ``rororo``.

Issues
======

Path Finder
-----------

There is known issue that default ``PathFinder`` from ``openapi-core`` library
matches more paths, then expected and as result return invalid operation, when
multiple paths in OpenAPI 3 schema matches current request path. Github issue:
`#226 <https://github.com/p1c2u/openapi-core/issues/226>`_

To fix this ``rororo`` uses its own ``PathFinder`` class, which should work in
most cases, but sometimes it might produce an error as well. In that case,
consider rename the path to avoid intersections with other paths in schema.

Nullable Schema
---------------

Even `#232 <https://github.com/p1c2u/openapi-core/issues/232>`_ is closed, it
is still not released, which may result in necessity of removing all
``nullable: true`` properties from the schema.
