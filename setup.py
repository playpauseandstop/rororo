# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['rororo', 'rororo.schemas']

package_data = \
{'': ['*']}

install_requires = \
['Sphinx[docs]>=1.8,<2.0',
 'aiohttp[tests]>=3.5,<4.0',
 'coverage[tests]>=4.5,<5.0',
 'coveralls[tests]>=1.7,<2.0',
 'fastjsonschema[tests]>=2.9,<3.0',
 'flake8-bugbear[lint]>=18.8,<19.0',
 'flake8-commas[lint]>=2.0,<3.0',
 'flake8-comprehensions[lint]>=2.1,<3.0',
 'flake8-docstrings[lint]>=1.3,<2.0',
 'flake8-import-order[lint]>=0.18.1,<0.19.0',
 'flake8-mutable[lint]>=1.2,<2.0',
 'flake8-quotes[lint]>=1.0,<2.0',
 'flake8-string-format[lint]>=0.2.3,<0.3.0',
 'flake8-tidy-imports[lint]>=2.0,<3.0',
 'flake8[lint]>=3.7,<4.0',
 'jsl[tests]>=0.2.4,<0.3.0',
 'jsonschema>=2.6,<3.0',
 'mypy[lint]>=0.670.0,<0.671.0',
 'pep8-naming[lint]>=0.8.2,<0.9.0',
 'sphinx_autodoc_typehints[docs]>=1.6,<2.0']

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
