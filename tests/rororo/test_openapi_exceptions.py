import pytest
from openapi_core.schema.exceptions import OpenAPIMappingError
from openapi_core.schema.media_types.exceptions import OpenAPIMediaTypeError
from openapi_core.schema.parameters.exceptions import OpenAPIParameterError

from rororo.openapi.exceptions import (
    BadRequest,
    ObjectDoesNotExist,
    OpenAPIError,
    ValidationError,
)


def test_bad_request():
    """
    Test for bad bad bad bad test.

    Args:
    """
    assert str(BadRequest()) == "Bad request"


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
    """
    Asserts that the test test test.

    Args:
        label: (str): write your description
        message: (str): write your description
        expected: (list): write your description
    """
    err = ObjectDoesNotExist(label, message=message)
    assert str(err) == expected


@pytest.mark.parametrize(
    "headers, expected", ((None, {}), ({"key": "value"}, {"key": "value"}))
)
def test_openapi_error_headers(headers, expected):
    """
    Test if the openapi.

    Args:
        headers: (dict): write your description
        expected: (todo): write your description
    """
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
    """
    Validate that the data.

    Args:
        data: (array): write your description
        expected: (todo): write your description
    """
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
    """
    Assert that the given dict has expected.

    Args:
        expected: (todo): write your description
    """
    err = ValidationError.from_dict(**kwargs)
    assert err.errors == expected


def test_validation_error_from_dict_value_error():
    """
    Validate the validation : parameter test results.

    Args:
    """
    with pytest.raises(ValueError):
        ValidationError.from_dict(
            {"body": "Missed"}, parameters={"name": "Parameter required"}
        )


@pytest.mark.parametrize(
    "method, error, expected_loc",
    (
        (ValidationError.from_request_errors, OpenAPIMappingError(), ["body"]),
        (
            ValidationError.from_response_errors,
            OpenAPIMappingError(),
            ["response"],
        ),
        (
            ValidationError.from_request_errors,
            OpenAPIMediaTypeError(),
            ["body"],
        ),
        (
            ValidationError.from_response_errors,
            OpenAPIMediaTypeError(),
            ["response"],
        ),
        (
            ValidationError.from_request_errors,
            OpenAPIParameterError(),
            ["body"],
        ),
        (
            ValidationError.from_response_errors,
            OpenAPIParameterError(),
            ["response"],
        ),
    ),
)
def test_validation_error_from_dummy_error(method, error, expected_loc):
    """
    Test if the expected error occurs.

    Args:
        method: (str): write your description
        error: (todo): write your description
        expected_loc: (todo): write your description
    """
    err = method([error])
    assert err.errors == [{"loc": expected_loc, "message": ""}]
    assert err.data == {"detail": [{"loc": expected_loc, "message": ""}]}
