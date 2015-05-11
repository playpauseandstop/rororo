import time

from random import choice
from unittest import TestCase

from jsonschema.exceptions import ValidationError
from jsonschema.validators import validate

from rororo.schemas import defaults, Error as SchemaError, Schema, Validator

import schemas


TEST_NAME = choice(('Igor', 'world'))


class TestSchema(TestCase):

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
