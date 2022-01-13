import pytest
from openapi_core.exceptions import (
    MissingRequestBodyError,
    OpenAPIParameterError,
)
from openapi_core.templating.media_types.exceptions import MediaTypeFinderError

from rororo.openapi.exceptions import (
    BadRequest,
    get_current_validation_error_loc,
    ObjectDoesNotExist,
    OpenAPIError,
    validation_error_context,
    ValidationError,
)


def test_bad_request():
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
    "method, error, expected_loc",
    (
        (
            ValidationError.from_request_errors,
            MissingRequestBodyError(),
            ["body"],
        ),
        (
            ValidationError.from_response_errors,
            MissingRequestBodyError(),
            ["response"],
        ),
        (
            ValidationError.from_request_errors,
            MediaTypeFinderError(),
            ["body"],
        ),
        (
            ValidationError.from_response_errors,
            MediaTypeFinderError(),
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
    err = method([error])
    assert err.errors == [{"loc": expected_loc, "message": ""}]
    assert err.data == {"detail": [{"loc": expected_loc, "message": ""}]}


def test_validation_error_message_no_errors():
    error = ValidationError(message="Validation error")
    assert error.errors is None


def test_validation_error_message_with_context():
    with validation_error_context("body", "user", "password"):
        assert ValidationError(message="Required field").errors == [
            {"loc": ["body", "user", "password"], "message": "Required field"}
        ]


def test_validation_error_erorrs_with_context():
    with validation_error_context("body", "user"):
        error = ValidationError(
            errors=[{"loc": ["password"], "message": "Required field"}]
        )
        assert error.errors == [
            {"loc": ["body", "user", "password"], "message": "Required field"}
        ]


def test_validation_error_invalid_args():
    with validation_error_context("body", "user"):
        with pytest.raises(ValueError):
            ValidationError(
                message="Required field",
                errors=[{"loc": ["body"], "message": "Other"}],
            )


def test_validation_error_from_dict():
    error = ValidationError.from_dict(
        body={"data": {0: {"item": "Required field"}}}
    )
    assert error.errors == [
        {"loc": ["body", "data", 0, "item"], "message": "Required field"}
    ]


def test_validation_error_from_dict_with_context():
    with validation_error_context("body", "data"):
        assert ValidationError.from_dict(field="Required field").errors == [
            {"loc": ["body", "data", "field"], "message": "Required field"}
        ]


def test_validation_error_empty_with_context():
    with validation_error_context("body", "data"):
        assert ValidationError().errors is None


def test_validation_error_add():
    first_error = ValidationError.from_dict(body={"field1": "Required field"})
    second_error = ValidationError.from_dict(body={"field2": "Required field"})

    expected_errors = [
        {"loc": ["body", "field1"], "message": "Required field"},
        {"loc": ["body", "field2"], "message": "Required field"},
    ]
    assert (first_error + second_error).errors == expected_errors


def test_validation_error_add_value_error():
    first_error = ValidationError(message="Validation error")
    second_error = ValidationError.from_dict(body={"field2": "Required field"})

    with pytest.raises(ValueError):
        first_error + second_error

    with pytest.raises(ValueError):
        second_error + first_error


def test_get_current_validation_error_loc():
    assert get_current_validation_error_loc() == ()

    with validation_error_context("body"):
        assert get_current_validation_error_loc() == ("body",)

        with validation_error_context("data", 0, "item"):
            assert get_current_validation_error_loc() == (
                "body",
                "data",
                0,
                "item",
            )

        assert get_current_validation_error_loc() == ("body",)

    assert get_current_validation_error_loc() == ()
