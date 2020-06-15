===========
simulations
===========

Simulations example to cover support of nullable data within *rororo*. As well
as directly passing schema & spec into ``setup_openapi``.

Usage
=====

.. code-block:: bash

    make EXAMPLE=simulations example

**IMPORTANT:** To run from *rororo* root directory.

Swagger UI
----------

To consume the API via `Swagger UI <https://swagger.io/tools/swagger-ui/>`_
run next command,

.. code-block:: bash

    docker run --rm -e URL="http://localhost:8080/openapi.yaml" \
        -h localhost -p 8081:8080 swaggerapi/swagger-ui:v3.25.0

After, open http://localhost:8081/ in your browser to access Swagger UI.
