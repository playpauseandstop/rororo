#!/usr/bin/env python

import os
import re

from pathlib import Path
from setuptools import setup


rel = Path(__file__).parent


with open(str(rel / 'README.rst')) as handler:
    README = handler.read()

with open(str(rel / 'rororo' / '__init__.py')) as handler:
    INIT_PY = handler.read()

VERSION = re.findall("__version__ = '([^']+)'", INIT_PY)[0]


setup(
    name='rororo',
    version=VERSION,
    description=(
        'Collection of utilities, helpers, and principles for building Python '
        'backend applications. Supports aiohttp.web, Flask, and your '
        'web-framework'
    ),
    long_description=README,
    author='Igor Davydenko',
    author_email='playpauseandstop@gmail.com',
    url='http://github.com/playpauseandstop/rororo',
    packages=[
        'rororo',
        'rororo.schemas',
    ],
    install_requires=[
        'jsonschema>=2.4.0,<3.0',
    ],
    platforms='any',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Utilities',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'License :: OSI Approved :: BSD License',
    ],
    keywords='utilities helpers principles aiohttp flask web framework',
    license='BSD License',
)
