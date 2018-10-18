"""
==============
test_timedelta
==============

Test timedelta utility functions.

"""

import datetime
from unittest import TestCase

from rororo.timedelta import (
    str_to_timedelta,
    timedelta_average,
    timedelta_div,
    timedelta_seconds,
    timedelta_to_str,
)


class TestTimedelta(TestCase):

    def test_str_to_timedelta_default(self):
        self.assertEqual(
            str_to_timedelta('10:00'),
            datetime.timedelta(hours=10))

    def test_str_to_timedelta_multiple_formats(self):
        self.assertEqual(
            str_to_timedelta('10:20', ('F', 'f', 'G:i')),
            datetime.timedelta(hours=10, minutes=20))

    def test_str_to_timedelta_user_format(self):
        self.assertEqual(
            str_to_timedelta('10:20:30', 'G:i:s'),
            datetime.timedelta(hours=10, minutes=20, seconds=30))

    def test_str_to_timedelta_wrong_format(self):
        with self.assertRaises(ValueError):
            str_to_timedelta('10:00', 'abc')

    def test_str_to_timedelta_wrong_value(self):
        with self.assertRaises(ValueError):
            str_to_timedelta(datetime.timedelta())

        with self.assertRaises(ValueError):
            str_to_timedelta(10)

    def test_str_to_timedelta_wrong_value_for_default_format(self):
        self.assertIsNone(str_to_timedelta('wrong value'))

    def test_str_to_timedelta_wrong_value_for_user_format(self):
        with self.assertRaises(ValueError):
            self.assertIsNone(str_to_timedelta('wrong value', 'G:i'))

    def test_timedelta_average(self):
        first = datetime.timedelta(hours=2)
        second = datetime.timedelta(hours=4)
        third = datetime.timedelta(hours=6)

        self.assertEqual(timedelta_average(first, second, third), second)

    def test_timedelta_average_as_list_or_tuple(self):
        first = datetime.timedelta(hours=2)
        second = datetime.timedelta(hours=4)
        third = datetime.timedelta(hours=6)

        with self.subTest('list'):
            self.assertEqual(timedelta_average([first, second, third]), second)

        with self.subTest('tuple'):
            self.assertEqual(timedelta_average((first, second, third)), second)

    def test_timedelta_div(self):
        first = datetime.timedelta(hours=2)
        second = datetime.timedelta(hours=4)

        self.assertEqual(timedelta_div(first, second), .5)

    def test_timedelta_div_empty(self):
        empty = datetime.timedelta()
        non_empty = datetime.timedelta(hours=1)

        with self.subTest('first'):
            self.assertEqual(timedelta_div(empty, non_empty), 0)

        with self.subTest('second'):
            self.assertEqual(timedelta_div(non_empty, empty), None)

    def test_timedelta_seconds(self):
        self.assertEqual(timedelta_seconds(datetime.timedelta(hours=1)), 3600)

    def test_timedelta_seconds_empty(self):
        self.assertEqual(timedelta_seconds(datetime.timedelta()), 0)

    def test_timedelta_seconds_multiple_days(self):
        value = datetime.timedelta(days=2, hours=4, minutes=5, seconds=20)
        self.assertEqual(timedelta_seconds(value), 187520)

    def test_timedelta_to_str(self):
        expected_dict = {
            'F': '1:20:30',
            'f': '1:20:30',
            'G:i': '1:20',
            'G:i:s': '1:20:30',
            'H:i': '01:20',
            'H:i:s': '01:20:30',
            'R': '1:20:30',
            'r': '1:20:30',
            's': '30',
        }
        value = datetime.timedelta(hours=1, minutes=20, seconds=30)

        for fmt, expected in expected_dict.items():
            with self.subTest(fmt=fmt):
                self.assertEqual(timedelta_to_str(value, fmt), expected)

    def test_timedelta_to_str_full_days(self):
        expected_dict = {
            'F': '1 day, 12:20:30',
            'f': '1d 12:20:30',
            'R': '1 day, 12:20:30',
            'r': '1d 12:20:30',
        }
        value = datetime.timedelta(hours=36, minutes=20, seconds=30)

        for fmt, expected in expected_dict.items():
            with self.subTest(fmt=fmt):
                self.assertEqual(timedelta_to_str(value, fmt), expected)

    def test_timedelta_to_str_full_no_seconds(self):
        expected_dict = {
            'F': '2 weeks, 0:00',
            'f': '2w 0:00',
            'R': '14 days, 0:00:00',
            'r': '14d 0:00:00',
        }
        value = datetime.timedelta(hours=336)

        for fmt, expected in expected_dict.items():
            with self.subTest(fmt=fmt):
                self.assertEqual(timedelta_to_str(value, fmt), expected)

    def test_timedelta_to_str_full_weeks(self):
        expected_dict = {
            'F': '1 week, 1:30',
            'f': '1w 1:30',
            'R': '7 days, 1:30:00',
            'r': '7d 1:30:00',
        }
        value = datetime.timedelta(hours=169, minutes=30)

        for fmt, expected in expected_dict.items():
            with self.subTest(fmt=fmt):
                self.assertEqual(timedelta_to_str(value, fmt), expected)

    def test_timedelta_to_str_default(self):
        self.assertEqual(
            timedelta_to_str(datetime.timedelta(days=1, hours=2)),
            '26:00')

    def test_timedelta_to_str_wrong_value(self):
        with self.assertRaises(ValueError):
            timedelta_to_str('10:20')

        with self.assertRaises(ValueError):
            timedelta_to_str(datetime.date.today())

        with self.assertRaises(ValueError):
            timedelta_to_str(datetime.datetime.utcnow())
