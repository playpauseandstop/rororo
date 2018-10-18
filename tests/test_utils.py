"""
==========
test_utils
==========

Test rororo utility functions.

"""

from unittest import TestCase

from rororo.utils import to_bool, to_int


class TestUtils(TestCase):

    def test_to_bool(self):
        self.assertTrue(to_bool('1'))
        self.assertFalse(to_bool('0'))
        self.assertTrue(to_bool('y'))
        self.assertFalse(to_bool('n'))
        self.assertTrue(to_bool(1))
        self.assertFalse(to_bool(0))
        self.assertTrue(to_bool([1, 2, 3]))
        self.assertFalse(to_bool([]))

    def test_to_int(self):
        self.assertEqual(to_int(1), 1)
        self.assertEqual(to_int('1'), 1)
        self.assertIsNone(to_int('does not int'))
        self.assertEqual(to_int('does not int', 10), 10)
