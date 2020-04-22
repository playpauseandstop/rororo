==========
rororo API
==========

OpenAPI
=======

.. automodule:: rororo.openapi
.. autofunction:: rororo.openapi.setup_openapi
.. autoclass:: rororo.openapi.OperationTableDef
.. autofunction:: rororo.openapi.openapi_context
.. autofunction:: rororo.openapi.get_openapi_context
.. autofunction:: rororo.openapi.get_openapi_schema
.. autofunction:: rororo.openapi.get_openapi_spec
.. autofunction:: rororo.openapi.get_validated_data
.. autofunction:: rororo.openapi.get_validated_parameters

.. automodule:: rororo.openapi.data
.. autoclass:: rororo.openapi.data.OpenAPIContext

Settings
========

.. automodule:: rororo.settings
.. autoclass:: rororo.settings.BaseSettings
.. autofunction:: rororo.settings.setup_settings_from_environ
.. autofunction:: rororo.settings.setup_settings
.. autofunction:: rororo.settings.setup_locale
.. autofunction:: rororo.settings.setup_logging
.. autofunction:: rororo.settings.setup_timezone
.. autofunction:: rororo.settings.immutable_settings
.. autofunction:: rororo.settings.is_setting_key
.. autofunction:: rororo.settings.inject_settings
.. autofunction:: rororo.settings.iter_settings
.. autofunction:: rororo.settings.from_env

Logger
======

.. automodule:: rororo.logger
.. autofunction:: rororo.logger.default_logging_dict
.. autofunction:: rororo.logger.update_sentry_logging
.. autoclass:: rororo.logger.IgnoreErrorsFilter
    :members:

aio-libs Utils
==============

.. automodule:: rororo.aio
    :members:

Timedelta Utils
===============

.. automodule:: rororo.timedelta
    :members:

Other Utilities
===============

.. automodule:: rororo.utils
    :members:
