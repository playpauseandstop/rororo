==================================
Known OpenAPI limitations & issues
==================================

There are some limitations & issues in providing OpenAPI 3 support for
aiohttp.web applications via *rororo* library.

.. important::
    In case, if your issue not listed below, feel free to open
    `new issue <https://github.com/playpauseandstop/rororo/issues/new>`_ at
    GitHub.

Limitations
===========

Unsupported Security Schemes
----------------------------

As of ``2.0.0rc3`` release
`OAuth2 <https://swagger.io/docs/specification/authentication/oauth2/>`_ &
`OpenID <https://swagger.io/docs/specification/authentication/openid-connect-discovery/>`_
security schemes is not supported. And at a moment there is no plans of adding
support of given security schemes to *rororo*.

Issues
======

Path Finder
-----------

There is known issue that default ``PathFinder`` from ``openapi-core`` library
matches more paths, then expected and as result return invalid operation, when
multiple paths in OpenAPI 3 schema matches current request path. Github issue:
`openapi-core#226 <https://github.com/p1c2u/openapi-core/issues/226>`_

To fix this *rororo* uses its own ``PathFinder`` class, which should work in
most cases, but sometimes it might produce an error as well. In that case,
consider rename the path to avoid intersections with other paths in schema.

Nullable Data
-------------

``openapi-core`` has issues with handling nullable arrays & objects,

- `openapi-core#232 <https://github.com/p1c2u/openapi-core/issues/232>`_
- `openapi-core#251 <https://github.com/p1c2u/openapi-core/issues/251>`_

While `openapi-core#232`_ already fixed it is not yet releasesd to PyPI, which
requires *rororo* to implement own way on handling nullable data by providing
custom ``ArrayUnmarshaller`` & ``ObjectUnmarshaller`` instances.

In most cases it should work fine, but if you will experience any issues with
nullable data, feel free to update
`#85 <https://github.com/playpauseandstop/rororo/issues/85>`_ issue about
the subject.
