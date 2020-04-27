============================
Speed up rororo applications
============================

There are several known ways of improving performance for rororo applications.

[startup] Custom schema loader
==============================

In most cases you may ignore speeding up startup of aiohttp.web application,
the place where :func:`rororo.openapi.setup_openapi` called. But, as loading
schema dict from file is time consuming operation (especially when OpenAPI
schema file is large or disk, where file is stored, is slow) there are several
techniques on how to faster load OpenAPI schema.

YAML files
----------

Ensure that `libyaml <https://pyyaml.org/wiki/LibYAML>`_ is installed in your
system. After, ``yaml.CSafeLoader`` will be used instead of
``yaml.SafeLoader``, which might increase load time up to 10 times.

::

    In [1]: import yaml

    In [2]: from api.constants import PROJECT_PATH

    In [3]: schema_path = PROJECT_PATH / "openapi.yaml"

    In [4]: %timeit yaml.load(schema_path.read_text(), Loader=yaml.SafeLoader)
    164 ms ± 10.1 ms per loop (mean ± std. dev. of 7 runs, 10 loops each)

    In [5]: %timeit yaml.load(schema_path.read_text(), Loader=yaml.CSafeLoader)
    14.6 ms ± 339 µs per loop (mean ± std. dev. of 7 runs, 100 loops each)

JSON files
----------

:func:`rororo.openapi.setup_openapi` allows to pass custom schema loader
function, as by default, for JSON files, it uses standard :func:`json.loads`,
which is not the fastest way of loading JSON files into the Python.

Example below illustrates how to use `ujson <https://pypi.org/project/ujson/>`_
for loading schema from ``openapi.json`` file,

.. code-block:: python

    from pathlib import Path

    import ujson
    from aiohttp import web
    from rororo import setup_openapi

    from .views import operations


    app = setup_openapi(
        web.Application(),
        Path(__file__) / "openapi.json",
        operations,
        schema_loader=ujson.loads,
    )

[runtime] Disable validating responses
======================================

To satisfy that OpenAPI hander provides proper response ``rororo`` internally
run ``ResponseValidator.validate(...)`` function.

In most cases this fact is OK as it will ensure that all responses conform
OpenAPI schema and client will receive expected result. However, it also
results in extra deserializing / validation calls, which will slow down process
of getting response from OpenAPI handler.

To "fix" this, there is a possibility to entirely turn off validation of
responses in ``rororo``,

.. code-block:: python

    app = setup_openapi(
        web.Application(),
        Path(__file__) / "openapi.yaml",
        operations,
        is_validate_response=False,
    )

.. danger::
    Turning off response validation may cause **unexpected** results for
    application consumers.
