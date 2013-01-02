#!/usr/bin/env python

from setuptools import setup


README = open('README.rst').read()
VERSION = '0.1'

setup(
    name='rororo',
    version=VERSION,
    description='Functional nano web-framework built on top of WebOb, routr ' \
                'and Jinja',
    long_description=README,
    author='Igor Davydenko',
    author_email='playpauseandstop@gmail.com',
    url='http://github.com/playpauseandstop/rororo',
    packages=[
        'rororo',
    ],
    install_requires=[
        'Jinja2>=2.6',
        'WebOb>=1.2.3',
        'routr==0.6.2',
        'routr-schema==0.1',
        'schemify==0.1',
        'server-reloader>=0.1.2',
    ],
    test_suite='rororo.tests',
    platforms='any',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Operating System :: OS Independent',
        'Topic :: Utilities',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'License :: OSI Approved :: BSD License',
    ],
    keywords='nano web framework webob routr jinja',
    license='BSD License',
)
