import os
import tempfile

from unittest import TestCase

from webtest import TestApp

from rororo import GET, create_app, exceptions
from rororo.exceptions import ImproperlyConfigured
from rororo.manager import manage


DEBUG = True
TEMPLATE = '<p>{{ var }}</p>'
TEMPLATE_DIR = os.path.join(tempfile.gettempdir(), 'rororo')
TEMPLATE_NAME = 'template.html'

ROUTES = ('',
    GET('/', 'tests.index_view', name='index'),
    GET('/json', 'tests.json_view', name='json', renderer='json'),
    GET('/server-error-1', 'tests.server_error_view', name='server_error'),
    GET('/server-error-2', 'tests.index_view', renderer='error'),
    GET('/template',
        'tests.template_view',
        name='template',
        renderer=TEMPLATE_NAME),
)


class TestRororo(TestCase):

    def setUp(self):
        if not os.path.isdir(TEMPLATE_DIR):
            os.mkdir(TEMPLATE_DIR)

        template = os.path.join(TEMPLATE_DIR, TEMPLATE_NAME)

        if not os.path.isfile(template):
            with open(template, 'w+') as handler:
                handler.write(TEMPLATE)

    def test_create_app(self):
        app = create_app(__name__)
        self.assertTrue(callable(app), repr(app))

    def test_create_app_default_settings(self):
        app = create_app(routes=ROUTES)
        self.assertEqual(app.settings.APP_DIR, os.getcwdu())
        self.assertFalse(app.settings.DEBUG)
        self.assertEqual(app.settings.JINJA_OPTIONS, {})
        self.assertEqual(app.settings.RENDERERS, ())
        self.assertEqual(app.settings.TEMPLATE_DIR, 'templates')

    def test_create_app_improperly_configured(self):
        self.assertRaises(ImproperlyConfigured, create_app)
        self.assertRaises(ImproperlyConfigured, create_app, exceptions)
        self.assertRaises(ImproperlyConfigured, create_app, routes={})

    def test_create_app_multiple_apps(self):
        routes = ('', GET('/', index_view))
        text_app = create_app(routes=routes)

        routes = ('', GET('/', json_view, renderer='json'))
        json_app = create_app(routes=routes)

        self.assertNotEqual(text_app.routes, json_app.routes)
        self.assertNotEqual(text_app.settings, json_app.settings)

    def test_routing_and_renderers(self):
        app = TestApp(create_app(__name__))

        response = app.get('/', status=200)
        self.assertEqual(response.text, 'Hello, world!')

        response = app.get('/json', status=200)
        self.assertEqual(response.json, {'var': 'Hello, world!'})

        response = app.get('/template', status=200)
        self.assertEqual(response.text, '<p>Hello, world!</p>')

        app.get('/does_not_exists.exe', status=404)
        app.get('/server-error-1', status=500)
        app.get('/server-error-2', status=500)

    def test_server_error(self):
        app = TestApp(create_app(__name__))

        response = app.get('/server-error-1', status=500)
        self.assertIn('Test Exception', response.text)

        response = app.get('/server-error-2', status=500)
        self.assertIn("Renderer 'error' does not exist.", response.text)

    def test_server_error_debug(self):
        app = TestApp(create_app(debug=False, routes=ROUTES))
        response = app.get('/server-error-1', status=500)
        self.assertNotIn('Traceback', response.text)

        app = TestApp(create_app(debug=True, routes=ROUTES))
        response = app.get('/server-error-1', status=500)
        self.assertIn('Traceback', response.text)


def index_view():
    return 'Hello, world!'


def json_view():
    return {'var': 'Hello, world!'}


def server_error_view():
    raise Exception('Test Exception')


def template_view():
    return {'var': 'Hello, world!'}
