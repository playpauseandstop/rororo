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


@pytest.mark.parametrize(
    "data, expected",
    (
        ({}, []),
        (
            {"body": "Validation error"},
            [{"loc": ["body"], "message": "Validation error"}],
        ),
        (
            {
                0: {
                    "item": {
                        "data": {
                            "tags": {
                                0: {"name": "Field required"},
                                1: {"description": "Is not unique"},
                            }
                        }
                    }
                },
                10: {"item": "Is empty"},
            },
            [
                {
                    "loc": [0, "item", "data", "tags", 0, "name"],
                    "message": "Field required",
                },
                {
                    "loc": [0, "item", "data", "tags", 1, "description"],
                    "message": "Is not unique",
                },
                {"loc": [10, "item"], "message": "Is empty"},
            ],
        ),
    ),
)
def test_validation_error_from_dict_data(data, expected):
    err = ValidationError.from_dict(data)
    assert err.errors == expected


@pytest.mark.parametrize(
    "kwargs, expected",
    (
        ({}, []),
        ({"body": "Missed"}, [{"loc": ["body"], "message": "Missed"}]),
    ),
)
def test_validation_error_from_dict_kwargs(kwargs, expected):
    err = ValidationError.from_dict(**kwargs)
    assert err.errors == expected


def test_validation_error_from_dict_value_error():
    with pytest.raises(ValueError):
        ValidationError.from_dict(
            {"body": "Missed"}, parameters={"name": "Parameter required"}
        )


@pytest.mark.parametrize(
    "method, error",
    (
        (ValidationError.from_request_errors, OpenAPIMappingError()),
        (ValidationError.from_response_errors, OpenAPIMappingError()),
        (ValidationError.from_request_errors, OpenAPIMediaTypeError()),
        (ValidationError.from_response_errors, OpenAPIMediaTypeError()),
        (ValidationError.from_request_errors, OpenAPIParameterError()),
        (ValidationError.from_response_errors, OpenAPIParameterError()),
    ),
)
def test_validation_error_from_dummy_error(method, error):
    err = method([error])
    assert err.errors == []
    assert err.data is None
