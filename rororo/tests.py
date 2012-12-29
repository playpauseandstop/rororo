import os
import tempfile

from unittest import TestCase

from rororo import GET, config, create_app, exceptions
from rororo.exceptions import ImproperlyConfigured
from rororo.manager import manage


TEMPLATE = '<p>{{ var }}</p>'
TEMPLATE_DIR = os.path.join(tempfile.gettempdir(), 'rororo')
TEMPLATE_NAME = 'template.html'

ROUTES = ('', (
    GET('/', 'tests.index_view', name='index'),
    GET('/json', 'tests.json_view', name='json'),
    GET('/template', 'tests.template_view', name=TEMPLATE_NAME),
))


class TestRororo(TestCase):

    def test_config(self):
        app = create_app(__name__)
        self.assertRaises(KeyError, config, 'TEMPLATE_DEBUG')
        config('TEMPLATE_DEBUG', True)
        self.assertTrue(config('TEMPLATE_DEBUG'))

    def test_create_app(self):
        app = create_app(__name__)
        self.assertTrue(callable(app), repr(app))

    def test_create_app_improperly_configured(self):
        self.assertRaises(ImproperlyConfigured, create_app, exceptions)

    def test_jinja(self):
        pass

    def test_renderer(self):
        pass

    def test_routing(self):
        pass


def index_view():
    return 'Hello, world!'


def json_view():
    return {'var': 'Hello, world!', 'rav': '!dlrow ,olleH'}


def template_view():
    return {'var': 'Hello world!'}
