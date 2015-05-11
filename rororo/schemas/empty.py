"""
====================
rororo.schemas.empty
====================

Collection of empty JSON Schemas, useful for validation empty requests or
responses.

"""

EMPTY_ARRAY = {
    'type': 'array',
    'maxItems': 0,
}
EMPTY_OBJECT = {
    'type': 'object',
    'additionalProperties': False,
}
