from unittest import TestCase

import six

from rororo.exceptions import HTTPNotFound
from webtest import TestApp

from app import app
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
        if six.PY3:
            self.client.get('/does_not_exist.exe', status=404)
        else:
            self.assertRaises(HTTPNotFound,
                              self.client.get,
                              '/does_not_exist.exe')

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
