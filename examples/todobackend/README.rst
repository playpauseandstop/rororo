============
Todo-Backend
============

`Todo-Backend <http://todobackend.com>`_ implementation built on top of
*rororo*, which highlights class based views usage.

Requirements
============

- `redis <https://redis.io>`_ 5.0 or later

Usage
=====

.. code-block:: bash

    make EXAMPLE=todobackend example

**IMPORTANT:** To run from *rororo* root directory.

After, feel free to run Todo-Backend tests by opening
http://www.todobackend.com/specs/index.html?http://localhost:8080/todos/ in
your browser.

Swagger UI
----------

To consume the API via `Swagger UI <https://swagger.io/tools/swagger-ui/>`_
run next command,

.. code-block:: bash

    docker run --rm -e URL="http://localhost:8080/todos/openapi.yaml" \
        -h localhost -p 8081:8080 swaggerapi/swagger-ui:v3.25.0

After, open http://localhost:8081/ in your browser to access Swagger UI.
