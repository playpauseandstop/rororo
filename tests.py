import uuid

from random import randint
from unittest import TestCase

from webtest import TestApp

from app import application, environ, hello, page, routes, search, \
    template_view


class TestRororo(TestCase):

    def test_environ(self):
        response = environ()
        self.assertTrue(response.json)
        self.assertEqual(response.headers['Content-Type'], 'application/json')

    def test_hello(self):
        response = hello()
        self.assertTrue(response.body, 'Hello, world!')

    def test_page(self):
        pk = randint(1000, 9999)
        response = page(pk)
        self.assertTrue(response.body, 'Page #{}!'.format(pk))

    def test_search(self):
        response = search()
        self.assertTrue(response.body, 'Enter query to search')

        query = str(uuid.uuid4())
        response = search(query)
        self.assertTrue(response.body, 'Searching {}...'.format(query))

    def test_template(self):
        response = template_view()
        self.assertIn('<h1>Hello, world!</h1>', response.body)
        self.assertIn('<pre>This is random string', response.body)
        self.assertIn(
            '<a href="{}">'.format(routes.reverse('hello')),
            response.body
        )


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
        self.assertTrue(response.text, 'Page #{:d}!'.format(pk))

    def test_search(self):
        response = self.client.get(self.url('search'), status=200)
        self.assertTrue(response.text, 'Enter query to search')

        query = str(uuid.uuid4())
        response = self.client.get(self.url('search', query=query), status=200)
        self.assertTrue(response.text, 'Searching {}...'.format(query))

    def test_template(self):
        response = self.client.get(self.url('template'), status=200)
        self.assertIn('<h1>Hello, world!</h1>', response.text)
        self.assertIn('<pre>This is random string', response.text)
        self.assertIn(
            '<p><a href="{}">'.format(self.url('hello')),
            response.text
        )
