#: Key to store OpenAPI schema within the ``web.Application`` instance
APP_OPENAPI_SCHEMA_KEY = "rororo_openapi_schema"

#: Key to store OpenAPI spec within the ``web.Application`` instance
APP_OPENAPI_SPEC_KEY = "rororo_openapi_spec"

#: Key to store request method -> operation ID mapping in handler
HANDLER_OPENAPI_MAPPING_KEY = "__rororo_openapi_mapping__"

#: Key to store current OpenAPI core operation within the ``web.Request``
#: instance
REQUEST_CORE_OPERATION_KEY = "rororo_core_operation"

#: Key to store current OpenAPI core request within the ``web.Request``
#: instance
REQUEST_CORE_REQUEST_KEY = "rororo_core_request"

#: Key to store valid OpenAPI context within the ``web.Request`` instance
REQUEST_OPENAPI_CONTEXT_KEY = "rororo_openapi_context"
