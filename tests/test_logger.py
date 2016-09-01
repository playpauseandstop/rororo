"""
===========
test_logger
===========

Test rororo logging utilities.

"""

from random import choice
from unittest import TestCase

from rororo.logger import (
    default_logging_dict,
    IgnoreErrorsFilter,
    update_sentry_logging,
)


TEST_SENTRY_DSN = 'https://username:password@app.getsentry.com/project-id'


class TestLogger(TestCase):

    def test_default_logging_dict(self):
        logging_dict = default_logging_dict('rororo')

        self.assertEqual(logging_dict['filters']['ignore_errors']['()'],
                         IgnoreErrorsFilter)

        self.assertEqual(len(logging_dict['formatters']), 2)
        self.assertIn('default', logging_dict['formatters'])
        self.assertIn('naked', logging_dict['formatters'])

        self.assertEqual(len(logging_dict['handlers']), 2)
        self.assertIn('stdout', logging_dict['handlers'])
        self.assertEqual(logging_dict['handlers']['stdout']['level'], 'DEBUG')
        self.assertIn('stderr', logging_dict['handlers'])
        self.assertEqual(logging_dict['handlers']['stderr']['level'],
                         'WARNING')

        self.assertEqual(len(logging_dict['loggers']), 1)
        self.assertIn('rororo', logging_dict['loggers'])
        self.assertEqual(logging_dict['loggers']['rororo']['handlers'],
                         ['stdout', 'stderr'])
        self.assertEqual(logging_dict['loggers']['rororo']['level'], 'INFO')

    def test_default_logging_dict_keyword_arguments(self):
        logging_dict = default_logging_dict('rororo', level='DEBUG')
        self.assertEqual(logging_dict['loggers']['rororo']['level'], 'DEBUG')

    def test_default_logging_dict_multiple_loggers(self):
        logging_dict = default_logging_dict('rororo', 'tests')

        self.assertEqual(len(logging_dict['loggers']), 2)
        self.assertIn('rororo', logging_dict['loggers'])
        self.assertIn('tests', logging_dict['loggers'])

    def test_ignore_errors_filter(self):
        filter_obj = IgnoreErrorsFilter()

        debug = type('FakeRecord', (object, ), {'levelname': 'DEBUG'})()
        info = type('FakeRecord', (object, ), {'levelname': 'INFO'})()
        warning = type('FakeRecord', (object, ), {'levelname': 'WARNING'})()
        error = type('FakeRecord', (object, ), {'levelname': 'ERROR'})()
        critical = type('FakeRecord', (object, ), {'levelname': 'CRITICAL'})()

        self.assertTrue(filter_obj.filter(debug))
        self.assertTrue(filter_obj.filter(info))
        self.assertFalse(filter_obj.filter(warning))
        self.assertFalse(filter_obj.filter(error))
        self.assertFalse(filter_obj.filter(critical))

    def test_update_sentry_logging(self):
        logging_dict = default_logging_dict('rororo')
        update_sentry_logging(logging_dict, TEST_SENTRY_DSN, 'rororo')
        self.assertIn('sentry', logging_dict['handlers'])
        self.assertIn('sentry', logging_dict['loggers']['rororo']['handlers'])

    def test_update_sentry_logging_empty_dsn(self):
        empty = choice((False, None, ''))

        logging_dict = default_logging_dict('rororo')
        update_sentry_logging(logging_dict, empty, 'rororo')

        self.assertNotIn('sentry', logging_dict['handlers'])
        self.assertNotIn('sentry',
                         logging_dict['loggers']['rororo']['handlers'])

    def test_update_sentry_logging_empty_loggers(self):
        logging_dict = default_logging_dict('rororo', 'tests')
        update_sentry_logging(logging_dict, TEST_SENTRY_DSN)
        self.assertIn('sentry', logging_dict['loggers']['rororo']['handlers'])
        self.assertIn('sentry', logging_dict['loggers']['tests']['handlers'])

    def test_update_sentry_logging_ignore_sentry(self):
        logging_dict = default_logging_dict('rororo', 'tests')
        logging_dict['loggers']['rororo']['ignore_sentry'] = True
        update_sentry_logging(logging_dict, TEST_SENTRY_DSN)
        self.assertNotIn('sentry',
                         logging_dict['loggers']['rororo']['handlers'])
        self.assertIn('sentry', logging_dict['loggers']['tests']['handlers'])

    def test_update_sentry_logging_kwargs(self):
        logging_dict = default_logging_dict('rororo')
        update_sentry_logging(logging_dict, TEST_SENTRY_DSN, key='value')
        self.assertEqual(logging_dict['handlers']['sentry']['key'], 'value')

    def test_update_sentry_logging_missed_logger(self):
        logging_dict = default_logging_dict('rororo')
        update_sentry_logging(logging_dict,
                              TEST_SENTRY_DSN,
                              'rororo',
                              'does-not-exist')
