# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['rororo', 'rororo.schemas']

package_data = \
{'': ['*']}

install_requires = \
['jsonschema>=2.6,<3.0']

setup_kwargs = {
    'name': 'rororo',
    'version': '1.2.1a0',
    'description': 'Collection of utilities, helpers, and principles for building Python backend applications. Supports aiohttp.web, Flask, and your web-framework',
    'long_description': '======\nrororo\n======\n\n.. image:: https://img.shields.io/circleci/project/github/playpauseandstop/rororo/master.svg\n    :target: https://circleci.com/gh/playpauseandstop/rororo\n    :alt: CircleCI\n\n.. image:: https://img.shields.io/pypi/v/rororo.svg\n    :target: https://pypi.org/project/rororo/\n    :alt: Latest Version\n\n.. image:: https://img.shields.io/pypi/pyversions/rororo.svg\n    :target: https://pypi.org/project/rororo/\n    :alt: Python versions\n\n.. image:: https://img.shields.io/pypi/l/rororo.svg\n    :target: https://github.com/playpauseandstop/rororo/blob/master/LICENSE\n    :alt: BSD License\n\n.. image:: https://coveralls.io/repos/playpauseandstop/rororo/badge.svg?branch=master&service=github\n    :target: https://coveralls.io/github/playpauseandstop/rororo\n    :alt: Coverage\n\n.. image:: https://readthedocs.org/projects/rororo/badge/?version=latest\n    :target: https://rororo.readthedocs.io/\n    :alt: Documentation\n\nCollection of utilities, helpers, and principles for building Python backend\napplications. Supports `aiohttp.web <http://aiohttp.readthedocs.org/>`_,\n`Flask <http://flask.pocoo.org/>`_, and your web-framework.\n\n* Works on Python 3.5+\n* BSD licensed\n* Latest documentation `on Read the Docs <https://rororo.readthedocs.org/>`_\n* Source, issues, and pull requests `on GitHub\n  <https://github.com/playpauseandstop/rororo>`_\n* Install with ``pip install rororo``\n',
    'author': 'Igor Davydenko',
    'author_email': 'iam@igordavydenko.com',
    'url': 'https://igordavydenko.com/projects.html#rororo',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5.3,<4.0.0',
}


setup(**setup_kwargs)
