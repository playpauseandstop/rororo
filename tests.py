import uuid

from random import randint
from unittest import TestCase

from webob.request import Request
from webtest import TestApp

from app import application, routes
from views import environ, hello, page, search, show_request, template


class TestRororo(TestCase):

    def test_environ(self):
        result = environ()
        self.assertIsInstance(result, dict)

    def test_hello(self):
        self.assertEqual(hello(), 'Hello, world!')

    def test_page(self):
        pk = randint(1000, 9999)
        self.assertEqual(page(pk), 'Page #{:d}'.format(pk))

    def test_search(self):
        self.assertTrue(search(), 'Enter query to search')

        query = str(uuid.uuid4())
        self.assertTrue(search(query), 'Searching {}...'.format(query))

    def test_show_request(self):
        request = Request.blank('/request')
        path = 'path.html'

        data = show_request(request, path)
        self.assertTrue(data)

        self.assertIn('path', data)
        self.assertEqual(data['path'], path)

        self.assertIn('method', data)
        self.assertEqual(data['method'], 'GET')

        self.assertIn('headers', data)

    def test_template(self):
        data = template()
        self.assertIn('var', data)


class TestRororoWithWebtest(TestCase):

    def setUp(self):
        self.client = TestApp(application)

    def url(self, url_rule, *args, **kwargs):
        return routes.reverse(url_rule, *args, **kwargs)

    def test_environ(self):
        response = self.client.get(self.url('environ'), status=200)
        self.assertTrue(response.json)

    def test_hello(self):
        response = self.client.get(self.url('hello'), status=200)
        self.assertTrue(response.text, 'Hello, world!')

    def test_page(self):
        pk = randint(1000, 9999)
        response = self.client.get(self.url('page', pk), status=200)
        self.assertTrue(response.text, 'Page #{:d}'.format(pk))

    def test_search(self):
        response = self.client.get(self.url('search'), status=200)
        self.assertTrue(response.text, 'Enter query to search')

        query = str(uuid.uuid4())
        response = self.client.get(self.url('search', query=query), status=200)
        self.assertTrue(response.text, 'Searching {}...'.format(query))

    def test_show_request(self):
        path = 'path.html'
        response = self.client.get(self.url('show_request', path), status=200)
        self.assertTrue(response.json)

        self.assertIn('path', response.json)
        self.assertEqual(response.json['path'], path)

        self.assertIn('method', response.json)
        self.assertEqual(response.json['method'], 'GET')

        self.assertIn('headers', response.json)

    def test_template(self):
        response = self.client.get(self.url('template'), status=200)
        self.assertIn('<h1>Hello, world!</h1>', response.text)
        self.assertIn('<pre>This is random string', response.text)
        self.assertIn(
            '<p><a href="{}">'.format(self.url('hello')),
            response.text
        )
