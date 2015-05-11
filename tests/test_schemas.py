import time
import types

from random import choice
from unittest import TestCase

from aiohttp.multidict import MultiDict, MultiDictProxy
from jsonschema.exceptions import ValidationError
from jsonschema.validators import validate

from rororo.schemas import defaults, Error as SchemaError, Schema, Validator
from rororo.schemas.empty import EMPTY_ARRAY, EMPTY_OBJECT

import schemas


TEST_NAME = choice(('Igor', 'world'))


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
