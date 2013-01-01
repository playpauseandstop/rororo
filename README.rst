======
rororo
======

.. image:: https://secure.travis-ci.org/playpauseandstop/rororo.png

Functional nano web-framework built on top of `WebOb <http://webob.org/>`_,
`routr <http://routr.readthedocs.com/>`_ and `Jinja <http://jinja.pocoo.org>`_.

Requirements
============

* `Python <http://www.python.org/>`_ 2.7
* `WebOb`_ 1.2.3 or higher
* `routr`_ 0.6.2
* `Jinja2`_ 2.6 or higher

Installation
============

As usual,

::

    # pip install rororo

Or if you want hard way, install it as you want and don't ask me why something
does not work.

For what reason?
================

Just to have little tool to fast creating WSGI applications. Little and easy
tool if you know what I mean. Prove?

::

    In [1]: from rororo import GET, create_app

    In [2]: from rororo.manager import run

    In [3]: view = lambda: 'Hello, world!'

    In [4]: app = create_app(routes=('', GET('/', view)))

    In [5]: run(app)
    Starting server at http://0.0.0.0:8000/

More?
=====

Coming soon...
