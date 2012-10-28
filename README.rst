======
rororo
======

.. image:: https://secure.travis-ci.org/playpauseandstop/rororo.png

Test project for `routr <http://pypi.python.org/pypi/routr>`_ library.

Requirements
============

* `Python <http://www.python.org/>`_ 2.6 or 2.7
* `Make <http://www.gnu.org/make>`_
* `virtualenv <http://virtualenv.org/>`_ 1.6 or higher
* `bootstrapper <http://pypi.python.org/pypi/bootstrapper>`_ 0.1 or higher

Installation
============

::

    $ make bootstrap

Usage
=====

Run development server with::

    $ make server

then point your browser to ``http://127.0.0.1:8080`` to see results.

----

To execute tests, run::

    $ make test
