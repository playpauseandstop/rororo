======
rororo
======

Collection of utilities, helpers, and principles for building Python backend
applications. Supports `aiohttp.web <http://aiohttp.readthedocs.org/>`_,
`Flask <http://flask.pocoo.org/>`_, and your web-framework.

* Works on Python 3.5+
* BSD licensed
* Source, issues, and pull requests `on GitHub
  <https://github.com/playpauseandstop/rororo>`_

Installation
============

.. code-block:: bash

    pip install rororo

License
=======

*rororo* is licensed under the terms of `BSD License
<https://github.com/playpauseandstop/rororo/blob/LICENSE>`_.

Schemas API
===========

.. automodule:: rororo.schemas

.. automodule:: rororo.schemas.schema
    :members:

.. automodule:: rororo.schemas.validators
    :members:

.. automodule:: rororo.schemas.utils
    :members:

Utilities API
=============

.. automodule:: rororo.settings
.. autofunction:: rororo.settings.immutable_settings
.. autofunction:: rororo.settings.is_setting_key
.. autofunction:: rororo.settings.inject_settings
.. autofunction:: rororo.settings.iter_settings
.. autofunction:: rororo.settings.from_env
.. autofunction:: rororo.settings.to_bool
.. autofunction:: rororo.settings.setup_locale
.. autofunction:: rororo.settings.setup_timezone

.. automodule:: rororo.logger
.. autofunction:: rororo.logger.default_logging_dict
.. autofunction:: rororo.logger.update_sentry_logging
.. autoclass:: rororo.logger.IgnoreErrorsFilter
    :members:

.. automodule:: rororo.aio
    :members:

Changelog
=========

.. include:: ../CHANGELOG.rst
