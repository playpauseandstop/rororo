import pytest
from openapi_core.schema.exceptions import OpenAPIMappingError
from openapi_core.schema.media_types.exceptions import OpenAPIMediaTypeError
from openapi_core.schema.parameters.exceptions import OpenAPIParameterError

from rororo.openapi.exceptions import (
    ObjectDoesNotExist,
    OpenAPIError,
    ValidationError,
)


@pytest.mark.parametrize(
    "label, message, expected",
    (
        (None, None, "None not found"),
        ("Phone", None, "Phone not found"),
        (None, "Message", "Message"),
        ("Phone", "Message", "Message"),
    ),
)
def test_object_does_not_exist(label, message, expected):
    err = ObjectDoesNotExist(label, message=message)
    assert str(err) == expected


@pytest.mark.parametrize(
    "headers, expected", ((None, {}), ({"key": "value"}, {"key": "value"}))
)
def test_openapi_error_headers(headers, expected):
    err = OpenAPIError(headers=headers)
    assert err.headers == expected


def test_validation_error_from_dummy_mapping_error():
    err = ValidationError.from_request_errors([OpenAPIMappingError()])
    assert err.errors == []
    assert err.data is None


def test_validation_error_from_dummy_media_type_error():
    err = ValidationError.from_request_errors([OpenAPIMediaTypeError()])
    assert err.errors == []
    assert err.data is None


def test_validation_error_from_dummy_operation_error():
    err = ValidationError.from_request_errors([OpenAPIParameterError()])
    assert err.errors == []
    assert err.data is None
