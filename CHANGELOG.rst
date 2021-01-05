2.2.0 (2021-01-05)
==================

**Features:**

- [#133] (**openapi**) Allow to pass kwargs to validate email func (#135)
- [#100, #132] (**openapi**) Improve validation errors (#142)

**Other:**

- Update dev Python version to 3.9.1 (#136)
- (**deps-dev**) bump pytest from 6.1.2 to 6.2.1 (#131)
- (**deps-dev**) bump coverage from 5.3 to 5.3.1 (#130)
- (**deps**) bump actions/checkout from v2.3.3 to v2.3.4 (#141)
- (**deps**) bump actions/cache from v2.1.2 to v2.1.3 (#138)
- (**deps**) bump actions/setup-python from v2.1.4 to v2.2.1 (#139)
- (**deps**) bump peter-evans/create-pull-request from v3.4.1 to v3.6.0 (#140)
- (**deps**) bump tibdex/github-app-token from v1.1.0 to v1.3 (#137)

2.1.3 (2020-12-09)
==================

**Fixes:**

- (**openapi**) Allow to use parameters within path object (#128)

**Other:**

- Several updates to pre-commit hooks (#122)
- (**deps**) bump aiohttp from 3.7.2 to 3.7.3 (#125)
- (**deps**) bump attrs from 20.2.0 to 20.3.0 (#126)
- (**deps**) bump email-validator from 1.1.1 to 1.1.2 (#124)

2.1.2 (2020-11-01)
==================

**Fixes:**

- Proper handling of operations with empty security list (#120)

**Other:**

- Improve examples & tests structure (#118)
- (**deps**) bump aiohttp from 3.6.3 to 3.7.2 (#119)

2.1.1 (2020-10-29)
==================

**Fixes:**

- (**openapi**) Proper handling of operations with empty security list (#115)

**Other:**

- Do not enforce commitizen check at CI (#113)

2.1.0 (2020-10-25)
==================

**Features:**

- Ensure Python 3.9 support (#109)

**Other:**

- (**deps**) bump attrs from 20.1.0 to 20.2.0 (#108)
- (**deps-dev**) bump pytest from 6.0.1 to 6.1.0 (#107)
- (**deps-dev**) bump coverage from 5.2.1 to 5.3 (#106)
- (**deps**) bump pyrsistent from 0.16.0 to 0.17.3 (#105)
- Integrate badabump for release needs (#110)

2.0.2 (2020-09-04)
==================

**Features:**

- Require ``attrs>=19.1,<21`` to allow use ``attrs==20.1.0`` in dependent
  projects

**Other:**

- Massive infrastrucutre update: move code to ``src/`` directory, use latest
  ``pytest`` for tests, better ``Makefile`` targets, etc

2.0.1 (2020-07-21)
==================

**Features:**

- Ensure *rororo* to work properly with ``openapi-core==0.13.4``

2.0.0 (2020-06-29)
==================

Final **2.0.0** release, which completes reimplementing *rororo* as library
for implementing aiohttp.web OpenAPI 3 server applications with schema first
approach.

**Quickstart:**

*rororo* relies on valid OpenAPI 3 schema (both JSON & YAML formats supported).
Example below illustrates using ``openapi.yaml`` schema file, stored next to
``app`` module,

.. code-block:: python

    from pathlib import Path
    from typing import List

    from aiohttp import web
    from rororo import setup_openapi

    from .views import operations


    def create_app(argv: List[str] = None) -> web.Application:
        return setup_openapi(
            web.Application(),
            Path(__file__).parent / "openapi.yaml",
            operations,
        )

Then, you need to *register* operation handlers in ``views`` module. Example
below shows registering handler for *operationId* ``hello_world``,

.. code-block:: python

    from aiohttp import web
    from rororo import OperationTableDef


    @operations.register
    async def hello_world(request: web.Request) -> web.Response:
        return web.json_response({"data": "Hello, world!"})

`Documentation <https://rororo.readthedocs.io/en/latest/openapi.html>`_
provides more information on implementing aiohttp.web OpenAPI 3 server
applications with schema first approach using *rororo*.

2.0.0rc3 (2020-06-15)
---------------------

**Features:**

- Allow passing ``schema`` and ``spec`` keyword args to ``setup_openapi``
  (`#84 <https://github.com/playpauseandstop/rororo/issues/84>`_)

**Fixes:**

- Handle all errors on creating OpenAPI spec from schema
  (`#74 <https://github.com/playpauseandstop/rororo/issues/74>`_)
- Allow nullable arrays & objects in request/response data
  (`#85 <https://github.com/playpauseandstop/rororo/issues/85>`_)

**Other:**

- Cast return values instead of type ignore comments
- Do not include changelog into dist
  (`#72 <https://github.com/playpauseandstop/rororo/issues/72>`_)
- Update docs with new rororo slogan
  (`#76 <https://github.com/playpauseandstop/rororo/issues/76>`_)
- Create GitHub release at pushing git tag
  (`#78 <https://github.com/playpauseandstop/rororo/issues/78>`_)
- Bump pre-commit hooks
- Preserve multiline strings in release body
  (`#78 <https://github.com/playpauseandstop/rororo/issues/78>`_)

2.0.0rc2 (2020-05-15)
---------------------

**Fixes:**

- When possible pass request body as string to ``OpenAPIRequest``, not as bytes

**Other:**

- Update pre-commit hooks, integrate ``flake8-variable-names`` check

2.0.0rc1 (2020-05-04)
---------------------

**Performance:**

- Use ``yaml.CSafeLoader`` instead of ``yaml.SafeLoader`` when possible. Allow
  to supply schema loader function to use custom loader, for example
  ``ujson.loads`` instead of ``json.loads``
- Use ``yaml.CSadeDumper`` instead of ``yaml.Dumper`` when possible on dumping
  OpenAPI schema when it is requested in YAML format
- Allow to cache create schema and spec call, usable for speeding up tests

**Other:**

- Use ``sphinx-autobuild`` for building docs at local env

2.0.0rc0 (2020-04-27)
---------------------

**Breaking Changes:**

- Use `environ-config <https://pypi.org/project/environ-config/>`_ for settings
  needs, instead of providing extra sugar to `attrs <https://www.attrs.org>`_

**Features:**

- Upgrade to latest ``openapi-core==0.13.3``
- Support class based views
- Deprecate old approach of validating OpenAPI requests via
  ``openapi_operation`` decorator in favor of ``openapi_middleware``.
  Improvements to error middleware, validate error responses against OpenAPI
  schema as well
- Valid request data is freezed with
  `pyrsistent.freeze <https://pyrsistent.readthedocs.io/en/latest/api.html#pyrsistent.freeze>`_
  call. Parameters and security data now wrapped into
  `pyrsistent.pmap <https://pyrsistent.readthedocs.io/en/latest/api.html#pyrsistent.pmap>`_
  for immutability needs
- Use `email-validator <https://pypi.org/project/email-validator/>`_ to support
  ``format: "email"``
- Ensure TZ aware date times works as expected
- Ensure support of optional security schemes

**Other:**

- Provide ``Todo-Backend`` example to illustrate how to use class based views
- Update pre-commit hooks, integrate ``blacken-docs`` & ``commitizen``
  pre-commit hooks
- Speed up CI exec time, by not waiting on build to start test job
- Add more badges to README

2.0.0b3 (2020-01-27)
--------------------

**Features:**

- Provide human readable security, request & response validation
  errors
- Support free form objects in request body
- Allow to enable CORS / error middleware on setting up OpenAPI support for
  ``aiohttp.web`` application
- Provide ``BaseSettings`` and ``env_factory`` helpers to work with settings
  within ``aiohttp.web`` applications. Cover how to work with settings at docs
  as well

**Other:**

- Stricter ``mypy`` config to ensure ``@operations.register`` is a typed
  decorator

2.0.0b2 (2019-12-19)
--------------------

**Other:**

- ``setup_openapi`` function returns ``web.Applicaiton`` instead of ``None``
- Provide ``ACCESS_LOG_FORMAT`` for ``aiohttp`` applications

2.0.0b1 (2019-11-20)
--------------------

**Fixes:**

- Fix type annotation for ``add_resource_context`` context manager

2.0.0b0 (2019-11-15)
--------------------

**Features:**

- Ensure Python 3.8 support. Move ``2.0.0`` release to beta phase

2.0.0a4 (2019-10-22)
--------------------

**Features:**

- Parse API Key & HTTP security data for OpenAPI operation
- Allow to remove root handlers on setting up logging config

**Other:**

- Cover ``rororo.openapi`` with non-machine docs
- Provide another example on using OpenAPI schema inside aiohttp.web application

2.0.0a3 (2019-10-09)
--------------------

**Features:**

- Support ``type: array`` request bodies as well
- Allow to validate responses against OpenAPI schema

**Other:**

- Do not directly depend on ``jsonschema``

2.0.0a2 (2019-10-08)
--------------------

**Fixes:**

- Depend on ``aiohttp>=3.5,<4.0``

2.0.0a1 (2019-10-08)
--------------------

**Features:**

- Add ``rororo.get_openapi_context`` shortcut

**Other:**

- Update API docs for ``rororo.openapi`` public functions & classes

2.0.0a0 (2019-10-08)
--------------------

**Breaking Changes:**

- Complete library rewrite

  - Instead of targeting any Python web framework, make ``rororo`` support only
    ``aiohttp.web`` applications
  - Build the library around the OpenAPI 3 schema support for ``aiohttp.web``
    applications
  - As result entirely remove ``rororo.schemas`` package from the project

1.2.1 (2019-07-08)
==================

- Publish 1.2.1 release

1.2.1a1 (2019-07-03)
--------------------

- chore: Introduce ``pre-commit`` hooks
- chore: Use ``pytest`` for tests
- chore: Use ``black`` for code formatting

1.2.1a0 (2019-02-24)
--------------------

- fix: Do not yet depend on ``jsonschema>=3.0.0``
- chore: Move ``tox.ini`` content into ``pyproject.toml``
- chore: Only use poetry for install project deps for tests & lint

1.2.0 (2018-11-01)
==================

- Publish 1.2.0 release

1.2.0a1 (2018-10-22)
--------------------

- Make all project packages `PEP-561 <https://www.python.org/dev/peps/pep-0561/>`_
  compatible

1.2.0a0 (2018-10-18)
--------------------

- Python 3.7 support
- Ensure that ``rororo`` works well with latest ``aiohttp``
- Allow setting ``level`` on updating logging dict to use Sentry handler
- Add new ``rororo.timedelta`` module with utilities to work with timedeltas
- Add new ``rororo.utils`` module
- Move type annotations to ``rororo.annotations`` module

1.1.1 (2017-10-09)
==================

- Do not attempt to convert empty list to dict for request/response data

1.1.0 (2017-10-09)
==================

- Allow to supply non-dicts in request/response data

1.0.0 (2017-05-14)
==================

- Publish 1.0 release, even proper docs are not ready yet

1.0.0b1 (2017-05-13)
--------------------

- Annotate all code in ``rororo``
- Use `mypy <http://mypy.readthedocs.io/>`_ on linting source code
- Require Python 3.5 or higher due to changes above

1.0.0a5 (2016-10-23)
--------------------

- Support validating schema via `fastjsonschema
  <http://opensource.seznam.cz/python-fastjsonschema/>`_ or any other validator

1.0.0a4 (2016-09-01)
--------------------

- Pass ``kwargs`` to ``SentryHandler`` on configuring Sentry logging

1.0.0a3 (2016-08-08)
--------------------

- Add ``rororo.aio`` module with:

  - ``add_resource_context`` context manager
  - ``is_xhr_request``, ``parse_aioredis_url`` utility functions

- Update flake8 config & bump aiohttp version for tests
- Added ChangeLog & modified GitHub Releases Page

1.0.0a2 (2015-12-18)
--------------------

- Adds ability to supply custom error class while making manual errors by
  ``schema.make_error`` method
- Default validator class preset default values from schema to instance for
  validation
- Several improvements to test process

1.0.0a1 (2015-11-26)
--------------------

- New beginning for rororo project. Now it is a bunch of helper methods instead
  of yet another web-framework.
