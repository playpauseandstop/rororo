import json
import time
import types

from random import choice
from unittest import TestCase

from aiohttp import web
from aiohttp.multidict import MultiDict, MultiDictProxy
from jsonschema.exceptions import ValidationError
from jsonschema.validators import validate

from rororo.schemas import defaults, Error as SchemaError, Schema, Validator
from rororo.schemas.empty import EMPTY_ARRAY, EMPTY_OBJECT

import schemas


TEST_NAME = choice(('Igor', 'world'))


class CustomError(Exception):

    """Custom Error."""


class TestEmpty(TestCase):

    def test_empty_array(self):
        validate([], EMPTY_ARRAY)
        self.assertRaises(ValidationError, validate, [1], EMPTY_ARRAY)

    def test_empty_object(self):
        validate({}, EMPTY_OBJECT)
        self.assertRaises(ValidationError,
                          validate,
                          {'key': 'value'},
                          EMPTY_OBJECT)


class TestSchema(TestCase):

    def check_wrapped_data(self, klass):
        schema = Schema(schemas.index)

        # Validate request should understand wrapped data
        base = {'name': TEST_NAME}
        wrapped = (klass(MultiDict(base))
                   if klass == MultiDictProxy
                   else klass(base))

        data = schema.validate_request(wrapped)
        self.assertEqual(data, base)
        self.assertIsInstance(data, klass)

        # Make response should understand wrapped data
        base = {'name': TEST_NAME, 'time': time.time()}
        wrapped = (klass(MultiDict(base))
                   if klass == MultiDictProxy
                   else klass(base))

        data = schema.make_response(wrapped)
        self.assertEqual(data, base)
        self.assertIsInstance(data, klass)

    def test_schema(self):
        schema = Schema(schemas.index)
        with self.assertRaises(SchemaError):
            raise schema.make_error('Dummy error')

        data = schema.validate_request({'name': TEST_NAME})
        self.assertEqual(data, {'name': TEST_NAME})

        timestamp = time.time()
        response = schema.make_response({'name': TEST_NAME, 'time': timestamp})
        self.assertEqual(response, {'name': TEST_NAME, 'time': timestamp})

    def test_schema_custom_error_class(self):
        schema = Schema(schemas.index, error_class=CustomError)

        with self.assertRaises(CustomError):
            raise schema.make_error('Custom Error')

        self.assertRaises(CustomError, schema.validate_request, {})
        schema.validate_request({'name': TEST_NAME})

        self.assertRaises(CustomError, schema.make_response, {})
        schema.make_response({'name': TEST_NAME, 'time': time.time()})

    def test_schema_custom_response_class(self):
        schema = Schema(schemas.project_page, response_factory=web.Response)
        schema.validate_request({'project_id': 1})
        response = schema.make_response(status=204)
        self.assertIsInstance(response, web.Response)
        self.assertEqual(response.status, 204)

    def test_schema_custom_response_factory(self):
        schema = Schema(schemas.index, response_factory=json_response_factory)
        schema.validate_request({'name': TEST_NAME})
        response = schema.make_response({'name': TEST_NAME,
                                         'time': time.time()})
        self.assertIsInstance(response, web.Response)
        self.assertEqual(response.content_type, 'application/json')

    def test_schema_empty_response(self):
        schema = Schema(schemas.null_response)
        schema.validate_request({})
        self.assertRaises(SchemaError, schema.make_response)
        self.assertRaises(SchemaError, schema.make_response, status=204)

    def test_schema_invalid_request(self):
        schema = Schema(schemas.index)
        self.assertRaises(ValidationError, schema.validate_request, {})
        self.assertRaises(ValidationError,
                          schema.validate_request,
                          {'name': 'Something'})
        self.assertRaises(SchemaError,
                          schema.make_response,
                          {'name': TEST_NAME, 'time': time.time()})

    def test_schema_make_response_request_not_validated(self):
        schema = Schema(schemas.index)
        self.assertRaises(SchemaError,
                          schema.make_response,
                          {'name': 'world', 'time': time.time()})

    def test_schema_mapping_proxy_type(self):
        self.check_wrapped_data(types.MappingProxyType)

    def test_schema_multi_dict(self):
        self.check_wrapped_data(MultiDict)

    def test_schema_multi_dict_proxy(self):
        self.check_wrapped_data(MultiDictProxy)

    def test_schema_multiple_request_data(self):
        schema = Schema(schemas.project_page)
        data = schema.validate_request(
            {'project_id': 1},
            {'project_id': 2, 'include_stories': True}
        )
        self.assertEqual(data, {'project_id': 1, 'include_stories': True})

    def test_schema_multiple_request_data_merged_class(self):
        schema = Schema(schemas.project_page)
        data = schema.validate_request(
            {'project_id': 1},
            {'archived': True},
            {'include_stories': False},
            merged_class=types.MappingProxyType
        )
        self.assertEqual(
            data,
            types.MappingProxyType({
                'project_id': 1,
                'archived': True,
                'include_stories': False,
            })
        )

    def test_schema_no_request_defined(self, module=None):
        schema = Schema(module or schemas.no_request)
        self.assertRaises(SchemaError, schema.validate_request, {})

    def test_schema_no_response_defined(self, module=None):
        schema = Schema(module or schemas.no_response)
        schema.validate_request({})
        data = schema.make_response({'dummy': True})
        self.assertEqual(data, {'dummy': True})

    def test_schema_null_request_defined(self):
        self.test_schema_no_request_defined(schemas.null_request)

    def test_schema_null_response_defined(self):
        self.test_schema_no_response_defined(schemas.null_response)


class TestValidator(TestCase):

    def test_tuple_is_array(self):
        schema = {
            'type': 'array',
            'items': {
                'type': 'number'
            },
            'minItems': 1,
            'maxItems': 3,
            'uniqueItems': True,
        }
        validate((1, 2, 3), schema, Validator)
        self.assertRaises(ValidationError,
                          validate,
                          tuple(),
                          schema,
                          Validator)
        self.assertRaises(ValidationError,
                          validate,
                          (1, 2, 3, 4),
                          schema,
                          Validator)
        # Temporary solution to use list instead of tuple, cause tuples cause
        # errors in unique items validator
        self.assertRaises(ValidationError, validate, [1, 1], schema, Validator)


class TestUtils(TestCase):

    def test_defaults(self):
        other = {'key': 'default-value', 'other-key': 'other-value'}
        data = defaults({'key': 'value'}, other)
        self.assertEqual(data, {'key': 'value', 'other-key': 'other-value'})

    def test_defaults_multiple(self):
        first = {'first': 1, 'second': 2}
        second = {'first': 0, 'second': 1, 'third': 2}
        data = defaults({'fourth': 3}, first, second)
        self.assertEqual(data,
                         {'first': 1, 'second': 2, 'third': 2, 'fourth': 3})


def json_response_factory(data):
    return web.Response(text=json.dumps(data), content_type='application/json')
