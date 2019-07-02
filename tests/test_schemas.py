import json
import time
import types
from random import choice

import fastjsonschema
import pytest
from aiohttp import web
from jsonschema.exceptions import ValidationError
from jsonschema.validators import validate
from multidict import MultiDict, MultiDictProxy

from rororo.schemas.empty import EMPTY_ARRAY, EMPTY_OBJECT
from rororo.schemas.exceptions import Error as SchemaError
from rororo.schemas.schema import Schema
from rororo.schemas.utils import defaults
from rororo.schemas.validators import DefaultValidator, Validator
from . import schemas


TEST_ARRAY = [1, 2, 3]
TEST_NAME = choice(("Igor", "world"))


class CustomError(Exception):

    """Custom Error."""


class FastSchemas(object):
    @property
    def request(self):
        return fastjsonschema.compile(schemas.index.request)

    @property
    def response(self):
        return fastjsonschema.compile(schemas.index.response)


def fast_validate(schema, data):
    return schema(data)


def json_response_factory(data):
    return web.Response(text=json.dumps(data), content_type="application/json")


def test_defaults():
    other = {"key": "default-value", "other-key": "other-value"}
    data = defaults({"key": "value"}, other)
    assert data == {"key": "value", "other-key": "other-value"}


def test_defaults_multiple():
    first = {"first": 1, "second": 2}
    second = {"first": 0, "second": 1, "third": 2}
    data = defaults({"fourth": 3}, first, second)
    assert data == {"first": 1, "second": 2, "third": 2, "fourth": 3}


def test_empty_array_ok():
    validate([], EMPTY_ARRAY)


def test_empty_array_fail():
    with pytest.raises(ValidationError):
        validate([1], EMPTY_ARRAY)


def test_empty_object_ok():
    validate({}, EMPTY_OBJECT)


def test_empty_object_fail():
    with pytest.raises(ValidationError):
        validate({"key": "value"}, EMPTY_OBJECT)


def test_schema():
    schema = Schema(schemas.index)
    with pytest.raises(SchemaError):
        raise schema.make_error("Dummy error")

    data = schema.validate_request({"name": TEST_NAME})
    assert data == {"name": TEST_NAME}

    timestamp = time.time()
    response = schema.make_response({"name": TEST_NAME, "time": timestamp})
    assert response == {"name": TEST_NAME, "time": timestamp}


def test_schema_array():
    schema = Schema(schemas.array)
    assert schema.validate_request(TEST_ARRAY) == TEST_ARRAY
    assert schema.make_response(TEST_ARRAY) == TEST_ARRAY


def test_schema_array_empty():
    schema = Schema(schemas.array)
    assert schema.validate_request([]) == []
    assert schema.make_response([]) == []


def test_schema_default_values():
    schema = Schema(schemas.default_values)
    data = schema.validate_request({})
    assert data == {"include_data_id": "0"}

    data = schema.make_response({"data": {"name": "Igor"}})
    assert data == {"data": {"name": "Igor", "main": False}, "system": "dev"}


def test_schema_default_values_override_defaults():
    schema = Schema(schemas.default_values)

    request_data = {"include_data_id": "1"}
    data = schema.validate_request(request_data)
    assert data == request_data

    response_data = {
        "data": {
            "name": "Igor",
            "uri": "http://igordavydenko.com/",
            "main": True,
        },
        "data_id": 1,
        "system": "production",
    }
    data = schema.make_response(response_data)
    assert data == response_data


def test_schema_custom_error_class():
    schema = Schema(schemas.index, error_class=CustomError)

    with pytest.raises(CustomError):
        raise schema.make_error("Custom Error")

    with pytest.raises(CustomError):
        schema.validate_request({})
    schema.validate_request({"name": TEST_NAME})

    with pytest.raises(CustomError):
        schema.make_response({})
    schema.make_response({"name": TEST_NAME, "time": time.time()})


def test_schema_custom_response_class():
    schema = Schema(schemas.project_page, response_factory=web.Response)
    schema.validate_request({"project_id": 1})
    response = schema.make_response(status=204)
    assert isinstance(response, web.Response)
    assert response.status == 204


def test_schema_custom_response_factory():
    schema = Schema(schemas.index, response_factory=json_response_factory)
    schema.validate_request({"name": TEST_NAME})
    response = schema.make_response({"name": TEST_NAME, "time": time.time()})
    assert isinstance(response, web.Response)
    assert response.content_type == "application/json"


def test_schema_custom_response_factory_empty_response():
    schema = Schema(
        schemas.project_page, response_factory=json_response_factory
    )
    schema.validate_request({"project_id": 1})
    response = schema.make_response({})
    assert isinstance(response, web.Response)
    assert response.content_type == "application/json"


@pytest.mark.parametrize("kwargs", ({}, {"status": 204}))
def test_schema_empty_response(kwargs):
    schema = Schema(schemas.null_response)
    schema.validate_request({})
    with pytest.raises(SchemaError):
        schema.make_response(**kwargs)


@pytest.mark.parametrize(
    "invalid_data",
    ({}, {"name": "Something"}, {"name": TEST_NAME, "time": time.time()}),
)
def test_schema_invalid_request(invalid_data):
    schema = Schema(schemas.index)
    with pytest.raises(ValidationError):
        schema.validate_request(invalid_data)


def test_shema_make_error_custom_error_class():
    schema = Schema(schemas.index)
    schema.validate_request({"name": "Igor"})
    with pytest.raises(CustomError, match="Something"):
        raise schema.make_error("Something", error_class=CustomError)


def test_schema_make_response_request_not_validated():
    schema = Schema(schemas.index)
    with pytest.raises(SchemaError):
        schema.make_response({"name": "world", "time": time.time()})


@pytest.mark.parametrize(
    "klass", (types.MappingProxyType, MultiDict, MultiDictProxy)
)
def test_schema_mapping_proxy_type(klass):
    schema = Schema(schemas.index)

    # Validate request should understand wrapped data
    base = {"name": TEST_NAME}
    wrapped = (
        klass(MultiDict(base)) if klass == MultiDictProxy else klass(base)
    )

    data = schema.validate_request(wrapped)
    assert data == base
    assert isinstance(data, klass)

    # Make response should understand wrapped data
    base = {"name": TEST_NAME, "time": time.time()}
    wrapped = (
        klass(MultiDict(base)) if klass == MultiDictProxy else klass(base)
    )

    data = schema.make_response(wrapped)
    assert data == base
    assert isinstance(data, klass)


def test_schema_multiple_request_data():
    schema = Schema(schemas.project_page)
    data = schema.validate_request(
        {"project_id": 1}, {"project_id": 2, "include_stories": True}
    )
    assert data == {"project_id": 1, "include_stories": True}


def test_schema_multiple_request_data_merged_class():
    schema = Schema(schemas.project_page)
    data = schema.validate_request(
        {"project_id": 1},
        {"archived": True},
        {"include_stories": False},
        merged_class=types.MappingProxyType,
    )
    proxy_data = types.MappingProxyType(
        {"project_id": 1, "archived": True, "include_stories": False}
    )
    assert data == proxy_data


@pytest.mark.parametrize("module", (schemas.no_request, schemas.null_request))
def test_schema_no_request_defined(module):
    schema = Schema(module)
    with pytest.raises(SchemaError):
        schema.validate_request({})


@pytest.mark.parametrize(
    "module", (schemas.no_response, schemas.null_response)
)
def test_schema_no_response_defined(module):
    schema = Schema(module)
    schema.validate_request({})
    data = schema.make_response({"dummy": True})
    assert data == {"dummy": True}


def test_fastjsonschema():
    error_class = fastjsonschema.JsonSchemaException
    schema = Schema(
        FastSchemas(),
        validate_func=fast_validate,
        validation_error_class=error_class,
    )

    # Default error
    with pytest.raises(SchemaError):
        raise schema.make_error("Dummy error")

    # Validation error propagated
    with pytest.raises(error_class):
        schema.validate_request({"name": "Something"})

    # Proper request
    data = schema.validate_request({"name": TEST_NAME})
    assert data == {"name": TEST_NAME}

    # Proper response
    # NOTE: fastjsonschema expects number as an int, not float
    timestamp = int(time.time())
    response = schema.make_response({"name": TEST_NAME, "time": timestamp})
    assert response == {"name": TEST_NAME, "time": timestamp}


def test_invalid_default_value():
    schema = {
        "properties": {"id": {"default": "Hello, world!", "type": "number"}}
    }
    with pytest.raises(ValidationError):
        DefaultValidator(schema).validate({})


def test_tuple_is_array():
    schema = {
        "type": "array",
        "items": {"type": "number"},
        "minItems": 1,
        "maxItems": 3,
        "uniqueItems": True,
    }
    validate((1, 2, 3), schema, Validator)

    with pytest.raises(ValidationError):
        validate((), schema, Validator)

    with pytest.raises(ValidationError):
        validate((1, 2, 3, 4), schema, Validator)

    # Temporary solution to use list instead of tuple, cause tuples cause
    # errors in unique items validator
    with pytest.raises(ValidationError):
        validate([1, 1], schema, Validator)
