#!/usr/bin/env python

import os
import re

from setuptools import setup


def rel(*parts):
    """Build relative path from given parts."""
    dirname = os.path.abspath(os.path.dirname(__file__))
    return os.path.abspath(os.path.join(dirname, *parts))


with open(rel('README.rst')) as handler:
    README = handler.read()

with open(rel('rororo', '__init__.py')) as handler:
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
    ],
    platforms='any',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Utilities',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'License :: OSI Approved :: BSD License',
    ],
    keywords='utilities helpers principles aiohttp flask web framework',
    license='BSD License',
)
