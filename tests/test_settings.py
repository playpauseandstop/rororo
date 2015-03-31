"""
=============
test_settings
=============

Test rororo Setting dictionary and additional utilities.

"""

import calendar
import datetime
import os

from unittest import TestCase

from rororo.settings import (
    from_env,
    immutable_settings,
    inject_settings,
    is_setting_key,
    setup_locale,
    setup_timezone,
    to_bool,
)

import settings as settings_module


TEST_DEBUG = True
TEST_USER = 'test-user'
_TEST_USER = 'private-user'


class TestSettings(TestCase):

    def setUp(self):
        setup_locale('en_US.UTF-8')
        setup_timezone('UTC')

    def check_immutability(self, settings):
        # Cannot update current value
        key = list(settings.keys())[0]
        with self.assertRaises(TypeError):
            settings[key] = 'new-value'

        # Cannot add new value
        self.assertNotIn('TEST_SETTING', settings)
        with self.assertRaises(TypeError):
            settings['TEST_SETTING'] = 'test-value'

        # Cannot update values at all
        with self.assertRaises(AttributeError):
            settings.update({key: 'new-value', 'TEST_SETTING': 'test_value'})

    def test_from_env(self):
        self.assertEqual(from_env('USER'), os.environ['USER'])
        self.assertIsNone(from_env('DOES_NOT_EXIST'))
        self.assertTrue(from_env('DOES_NOT_EXIST', True))

    def test_immutable_settings_from_dict(self):
        settings_dict = {'DEBUG': True,
                         'USER': 'test-user',
                         '_USER': 'private-user'}
        settings = immutable_settings(settings_dict)

        self.assertTrue(settings['DEBUG'])
        self.assertEqual(settings['USER'], 'test-user')
        self.assertNotIn('_USER', settings)

        settings_dict.pop('USER')
        self.assertEqual(settings['USER'], 'test-user')

        self.check_immutability(settings)

    def test_immutable_settings_from_globals(self):
        settings = immutable_settings(globals())

        self.assertTrue(settings['TEST_DEBUG'])
        self.assertEqual(settings['TEST_USER'], 'test-user')
        self.assertNotIn('_TEST_USER', settings)
        self.assertNotIn('TestCase', settings)

        self.check_immutability(settings)

    def test_immutable_settings_from_locals(self):
        DEBUG = True
        USER = 'test-user'
        _USER = 'private-user'

        settings = immutable_settings(locals())

        self.assertTrue(settings['DEBUG'])
        self.assertEqual(settings['USER'], 'test-user')
        self.assertNotIn('_USER', settings)
        self.assertNotIn('self', settings)

        del DEBUG, USER, _USER
        self.assertTrue(settings['USER'])

        self.check_immutability(settings)

    def test_immutable_settings_from_module(self):
        settings = immutable_settings(settings_module)

        self.assertTrue(settings['DEBUG'])
        self.assertEqual(settings['USER'], os.environ['USER'])
        self.assertNotIn('os', settings)

        self.check_immutability(settings)

    def test_immutable_settings_with_optionals(self):
        settings = immutable_settings(settings_module, DEBUG=False)
        self.assertFalse(settings['DEBUG'])
        self.assertEqual(settings['USER'], os.environ['USER'])

    def test_inject_settings_fail_silently(self):
        context = {}
        inject_settings('settings_error', context, True)
        self.assertEqual(context, {})

    def test_inject_settings_failed(self):
        context = {}
        self.assertRaises(NameError,
                          inject_settings,
                          'settings_error',
                          context)
        self.assertEqual(context, {})

    def test_inject_settings_from_dict(self):
        context = {'DEBUG': False}
        settings_dict = {'DEBUG': True, '_DEBUG': True}
        inject_settings(settings_dict, context)
        self.assertTrue(context['DEBUG'])
        self.assertNotIn('_DEBUG', context)

    def test_inject_settings_from_module(self):
        context = {'DEBUG': False}
        inject_settings(settings_module, context)
        self.assertTrue(context['DEBUG'])
        self.assertNotIn('os', context)

    def test_inject_settings_from_str(self):
        context = {'DEBUG': False}
        inject_settings('settings', context)
        self.assertTrue(context['DEBUG'])
        self.assertNotIn('os', context)

    def test_is_settings_key(self):
        self.assertTrue(is_setting_key('DEBUG'))
        self.assertTrue(is_setting_key('SECRET_KEY'))
        self.assertFalse(is_setting_key('_PRIVATE_USER'))
        self.assertFalse(is_setting_key('camelCase'))
        self.assertFalse(is_setting_key('secret_key'))

    def test_setup_locale(self):
        monday = calendar.day_abbr[0]
        first_weekday = calendar.firstweekday()

        setup_locale('ru_UA.UTF-8')
        self.assertNotEqual(calendar.day_abbr[0], monday)
        self.assertEqual(calendar.firstweekday(), first_weekday)

    def test_setup_locale_with_first_weekday(self):
        first_weekday = calendar.firstweekday()

        setup_locale('ru_UA.UTF-8', 1)
        self.assertEqual(calendar.firstweekday(), 1)

        setup_locale('en_US.UTF-8', first_weekday)

    def test_setup_timezone(self):
        setup_timezone('UTC')
        utc_now = datetime.datetime.now()

        setup_timezone('Europe/Kiev')
        kyiv_now = datetime.datetime.now()

        self.assertNotEqual(utc_now.hour, kyiv_now.hour)

    def test_setup_timezone_empty(self):
        previous = datetime.datetime.now()
        setup_timezone(None)
        self.assertEqual(previous.hour, datetime.datetime.now().hour)

    def test_setup_timezone_unknown(self):
        self.assertRaises(ValueError, setup_timezone, 'Unknown/Timezone')

    def test_to_bool(self):
        self.assertTrue(to_bool('1'))
        self.assertFalse(to_bool('0'))
        self.assertTrue(to_bool('y'))
        self.assertFalse(to_bool('n'))
        self.assertTrue(to_bool(1))
        self.assertFalse(to_bool(0))
        self.assertTrue(to_bool([1, 2, 3]))
        self.assertFalse(to_bool([]))
