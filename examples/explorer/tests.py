try:
    from unittest2 import TestCase
except ImportError:
    from unittest import TestCase

import sys

import six

from rororo.exceptions import HTTPNotFound
from webtest import TestApp

from app import app, settings
from views import explorer


class TestViews(TestCase):

    def test_does_not_exist(self):
        self.assertRaises(HTTPNotFound, explorer, '/does_not_exist')

    def test_exists(self):
        listing = explorer('')
        self.assertTrue(listing)


class TestWebTest(TestCase):

    def setUp(self):
        self.client = TestApp(app)

    def test_does_not_exist(self):
        if sys.version[:2] == (2, 6):
            self.assertRaises(HTTPNotFound,
                              self.client.get,
                              '/does_not_exist.exe')
        else:
            self.client.get('/does_not_exist.exe', status=404)

    def test_favicon(self):
        favicon = open(settings.rel('static', 'favicon.ico')).read()
        response = self.client.get('/favicon.ico', status=200)
        self.assertEqual(response.body, favicon)

    def test_index(self):
        response = self.client.get('/', status=200)
        self.assertIn('<title>File Explorer</title>', response.ubody)


class TestWebTestWithoutWdb(TestCase):

    def setUp(self):
        self.old_USE_WDB = app.settings.USE_WDB
        app.settings.USE_WDB = False

        self.client = TestApp(app)

    def tearDown(self):
        app.settings.USE_WDB = self.old_USE_WDB

    def test_does_not_exist(self):
        self.client.get('/does_not_exist.exe', status=404)
