# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rororo', 'rororo.openapi']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.1,<6.0',
 'aiohttp>=3.5,<4.0',
 'attrs>=19.1,<20.0',
 'jsonschema>=3.0,<4.0',
 'openapi-core>=0.12.0,<0.13.0']

setup_kwargs = {
    'name': 'rororo',
    'version': '2.0.0a2',
    'description': 'OpenAPI 3 schema support for aiohttp.web applications.',
    'long_description': '======\nrororo\n======\n\n.. image:: https://img.shields.io/circleci/project/github/playpauseandstop/rororo/feature-openapi.svg\n    :target: https://circleci.com/gh/playpauseandstop/rororo\n    :alt: CircleCI\n\n.. image:: https://img.shields.io/pypi/v/rororo.svg\n    :target: https://pypi.org/project/rororo/\n    :alt: Latest Version\n\n.. image:: https://img.shields.io/pypi/pyversions/rororo.svg\n    :target: https://pypi.org/project/rororo/\n    :alt: Python versions\n\n.. image:: https://img.shields.io/pypi/l/rororo.svg\n    :target: https://github.com/playpauseandstop/rororo/blob/master/LICENSE\n    :alt: BSD License\n\n.. image:: https://coveralls.io/repos/playpauseandstop/rororo/badge.svg?branch=feature-openapi&service=github\n    :target: https://coveralls.io/github/playpauseandstop/rororo\n    :alt: Coverage\n\n.. image:: https://readthedocs.org/projects/rororo/badge/?version=latest\n    :target: https://rororo.readthedocs.io/\n    :alt: Documentation\n\n`OpenAPI 3 <https://spec.openapis.org/oas/v3.0.2>`_ schema support\nfor `aiohttp.web <https://aiohttp.readthedocs.io/en/stable/web.html>`_\napplications.\n\nAs well as bunch other utilities to build effective web applications with\nPython 3 & ``aiohttp.web``.\n\n* Works on Python 3.6+\n* BSD licensed\n* Source, issues, and pull requests `on GitHub\n  <https://github.com/playpauseandstop/rororo>`_\n\nQuick Start\n===========\n\n``rororo`` relies on valid OpenAPI schema file (both JSON or YAML formats\nsupported).\n\nExample below, illustrates on how to handle operation ``hello_world`` from\n`openapi.yaml <https://github.com/playpauseandstop/rororo/blob/feature-openapi/tests/openapi.yaml>`_\nschema file.\n\n.. code-block:: python\n\n    from pathlib import Path\n\n    from aiohttp import web\n\n    from rororo import openapi_context, OperationTableDef, setup_openapi\n\n\n    operations = OperationTableDef()\n\n\n    @operations.register\n    async def hello_world(request: web.Request) -> web.Response:\n        with openapi_context(request) as context:\n            name = context.parameters.query.get("name", "world")\n            return web.json_response({"message": f"Hello, {name}!"})\n\n\n    def create_app(argv: List[str] = None) -> web.Application:\n        app = web.Application()\n        setup_openapi(\n            app,\n            Path(__file__).parent / "openapi.yaml",\n            operations,\n            route_prefix="/api"\n        )\n        return app\n\nCheck\n`examples <https://github.com/playpauseandstop/rororo/tree/feature-openapi/examples>`_\nfolder to see other examples on how to use OpenAPI 3 schemas with aiohttp.web\napplications.\n',
    'author': 'Igor Davydenko',
    'author_email': 'iam@igordavydenko.com',
    'url': 'https://igordavydenko.com/projects.html#rororo',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
