#!/usr/bin/env python

import os
import re
import sys

from setuptools import setup

DIRNAME = os.path.abspath(os.path.dirname(__file__))
rel = lambda *parts: os.path.abspath(os.path.join(DIRNAME, *parts))

README = open(rel('README.rst')).read()
INIT_PY = open(rel('rororo', '__init__.py')).read()
VERSION = re.findall("__version__ = '([^']+)'", INIT_PY)[0]


setup(
    name='rororo',
    version=VERSION,
    description=('Functional nano web-framework built on top of WebOb, routr '
                 'and Jinja'),
    long_description=README,
    author='Igor Davydenko',
    author_email='playpauseandstop@gmail.com',
    url='http://github.com/playpauseandstop/rororo',
    packages=[
        'rororo',
    ],
    install_requires=list(filter(None, [
        'Jinja2==2.6',
        'WebOb>=1.2.3',
        'argparse==1.2.1' if sys.version_info[:2] < (2, 7) else None,
        'routr>=0.7.1',
        'routr-schema>=0.1',
        'schemify>=0.1',
        'server-reloader>=0.1.2',
        'unittest2==0.5.1' if sys.version_info[:2] < (2, 7) else None,
    ])),
    platforms='any',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Utilities',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'License :: OSI Approved :: BSD License',
    ],
    keywords='nano web framework webob routr jinja',
    license='BSD License',
)
