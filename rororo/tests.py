# -*- coding: utf-8 -*-

import json
import os
import sys
import tempfile

from string import Template

try:
    from unittest2 import TestCase
except ImportError:
    from unittest import TestCase

import six

from jinja2.utils import escape
from routr import route
from webob.response import Response
from webtest import TestApp

from rororo import GET, create_app, exceptions, manage
from rororo.exceptions import ImproperlyConfigured, RouteReversalError
from rororo.utils import absdir, force_unicode


DEBUG = True
STATIC_DIR = TEMPLATE_DIR = os.path.join(tempfile.gettempdir(), 'rororo')
TEMPLATE = '<h1>{{ var }}</h1>'
TEMPLATE_NAME = 'template.html'
TEMPLATE_WITH_GLOBALS = """<h1>Hello, world!</h1>

<h2>Links</h2>
<ul>
    <li><a href="{{ reverse("index") }}">Index view</a></li>
    <li><a href="{{ reverse("lambda") }}">Lambda view</a></li>
    <li><a href="{{ reverse("json") }}">JSON view</a></li>
    <li><a href="{{ reverse("server_error") }}">Server Error view</a></li>
</ul>

<h2>Settings</h2>
<ul>
    <li>APP_DIR: {{ settings.APP_DIR }}</li>
    <li>DEBUG: {{ settings.DEBUG }}</li>
    <li>JINJA_OPTIONS: {{ settings.JINJA_OPTIONS }}</li>
    <li>RENDERERS: {{ settings.RENDERERS }}</li>
    <li>TEMPLATE_DIR: {{ settings.TEMPLATE_DIR }}</li>
</ul>
"""

RENDERERS = (
    ('custom_json', 'rororo.tests.custom_json_renderer'),
    ('custom_template', 'rororo.tests.custom_template_renderer'),
    ('wrong', Response),
)
ROUTES = (
    GET('/', 'rororo.tests.index_view', name='index'),
    GET('/json', 'rororo.tests.json_view', name='json', renderer='json'),
    GET('/json/custom', 'rororo.tests.json_view', renderer='custom_json'),
    GET('/lambda', lambda: 'Hello, world!', name='lambda', renderer='text'),
    GET('/server-error-1',
        'rororo.tests.server_error_view',
        name='server_error'),
    GET('/server-error-2', 'rororo.tests.index_view', renderer='error'),
    GET('/server-error-3', 'rororo.tests.index_view', renderer='wrong'),
    GET('/template',
        'rororo.tests.template_view',
        name='template',
        renderer=TEMPLATE_NAME),
    GET('/template/custom',
        'rororo.tests.template_view',
        renderer='custom_template'),
)


class TestRororo(TestCase):

    def setUp(self):
        if not os.path.isdir(STATIC_DIR):
            os.mkdir(STATIC_DIR)

        self.template = template = os.path.join(TEMPLATE_DIR, TEMPLATE_NAME)

        with open(template, 'w+') as handler:
            handler.write(TEMPLATE)

    def tearDown(self):
        if hasattr(self, 'old_argv'):
            sys.argv = self.old_argv

        if hasattr(self, 'old_stdout'):
            sys.stdout = self.old_stdout

        if hasattr(self, 'old_stderr'):
            sys.stderr = self.old_stderr

    def test_create_app(self):
        app = create_app(__name__)
        self.assertTrue(callable(app), repr(app))

    def test_create_app_default_settings(self):
        app = create_app(routes=ROUTES)
        self.assertEqual(app.settings.APP_DIR,
                         os.getcwdu() if not six.PY3 else os.getcwd())
        self.assertFalse(app.settings.DEBUG)
        self.assertEqual(app.settings.JINJA_GLOBALS, {})
        self.assertEqual(app.settings.JINJA_FILTERS, {})
        self.assertEqual(app.settings.JINJA_OPTIONS, {})
        self.assertEqual(app.settings.PACKAGES, ())
        self.assertEqual(app.settings.RENDERERS, ())
        self.assertEqual(app.settings.STATIC_DIR, 'static')
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

        self.assertNotEqual(text_app.reverse, json_app.reverse)
        self.assertNotEqual(text_app.routes, json_app.routes)
        self.assertNotEqual(text_app.settings, json_app.settings)

    def test_create_app_reverse(self):
        app = create_app(__name__)

        self.assertEqual(app.reverse('index'), '/')
        self.assertEqual(app.reverse('index'), '/')
        self.assertEqual(app.reverse('json'), '/json')
        self.assertEqual(app.reverse('server_error'), '/server-error-1')
        self.assertEqual(app.reverse('template'), '/template')
        self.assertRaises(RouteReversalError, app.reverse, 'does_not_exist')

        self.assertEqual(app.routes.reverse('index'), '/')
        self.assertEqual(app.routes.reverse('json'), '/json')
        self.assertEqual(app.routes.reverse('server_error'), '/server-error-1')
        self.assertEqual(app.routes.reverse('template'), '/template')
        self.assertRaises(RouteReversalError,
                          app.routes.reverse,
                          'does_not_exist')

    def test_jinja_renderer(self):
        dirname = os.path.abspath(os.path.dirname(__file__))

        with open(self.template, 'w+') as handler:
            handler.write(TEMPLATE_WITH_GLOBALS)

        app = TestApp(create_app(__name__))
        response = app.get('/template', status=200)

        self.assertIn('<a href="/">', response.text)
        self.assertIn('<a href="/json">', response.text)
        self.assertIn('<a href="/lambda">', response.text)
        self.assertIn('<a href="/server-error-1">', response.text)

        self.assertIn('APP_DIR: {0}'.format(dirname), response.text)
        self.assertIn('DEBUG: True', response.text)
        self.assertIn('JINJA_OPTIONS: {}', response.text)
        self.assertIn(
            'RENDERERS: {0}'.format(escape(RENDERERS)), response.text
        )
        self.assertIn(
            'TEMPLATE_DIR: {0}'.format(escape(TEMPLATE_DIR)), response.text
        )

        new_app = TestApp(create_app(routes=ROUTES, template_dir=TEMPLATE_DIR))
        response = new_app.get('/template', status=200)
        self.assertIn('DEBUG: False', response.text)
        self.assertIn('RENDERERS: ()', response.text)

        response = app.get('/template', status=200)
        self.assertIn('DEBUG: True', response.text)
        self.assertNotIn('RENDERERS: ()', response.text)

    def test_manage(self):
        self.old_argv = sys.argv
        self.old_stdout, self.old_stderr = sys.stdout, sys.stderr

        stdout, stderr = six.StringIO(), six.StringIO()
        sys.argv = [sys.argv[0]]
        sys.stdout, sys.stderr = stdout, stderr

        # Run manager without arguments
        app = create_app(__name__)

        try:
            manage(app)
        except SystemExit as err:
            self.assertEqual(err.code, 2)

        # Run clean_pyc management command
        sys.argv = [sys.argv[0], 'clean_pyc']

        try:
            manage(app)
        except SystemExit as err:
            self.assertEqual(err.code, 0)

        # Run print_settings management command
        sys.argv = [sys.argv[0], 'print_settings']

        try:
            manage(app)
        except SystemExit as err:
            self.assertEqual(err.code, 0)

        # Run undefined management command
        sys.argv = [sys.argv[0], 'does_not_exist']

        try:
            manage(app)
        except SystemExit as err:
            self.assertEqual(err.code, 2)

        # Run custom management command
        sys.argv = [sys.argv[0], 'custom_command']

        try:
            manage(app)
        except SystemExit as err:
            self.assertEqual(err.code, 2)

        try:
            manage(app, custom_command)
        except SystemExit as err:
            self.assertEqual(err.code, 0)

    def test_routing_and_renderers(self):
        app = TestApp(create_app(__name__))

        response = app.get('/', status=200)
        self.assertEqual(
            response.headers['Content-Type'], 'text/html; charset=UTF-8'
        )
        self.assertEqual(response.text, 'Hello, world!')

        response = app.get('/json', status=200)
        self.assertEqual(
            response.headers['Content-Type'], 'application/json; charset=UTF-8'
        )
        self.assertEqual(response.json, {'var': 'Hello, world!'})

        response = app.get('/json/custom', status=200)
        self.assertEqual(
            response.headers['Content-Type'], 'application/json; charset=UTF-8'
        )
        self.assertEqual(response.json, {'var': 'Hello, world!'})

        response = app.get('/lambda', status=200)
        self.assertEqual(
            response.headers['Content-Type'], 'text/plain; charset=UTF-8'
        )
        self.assertEqual(response.text, 'Hello, world!')

        response = app.get('/template', status=200)
        self.assertEqual(
            response.headers['Content-Type'], 'text/html; charset=UTF-8'
        )
        self.assertEqual(response.text, '<h1>Hello, world!</h1>')

        response = app.get('/template/custom', status=200)
        self.assertEqual(
            response.headers['Content-Type'], 'text/html; charset=UTF-8'
        )
        self.assertEqual(response.text, '<h1>Hello, world!</h1>')

        app.get('/does_not_exist.exe', status=404)
        app.get('/server-error-1', status=500)
        app.get('/server-error-2', status=500)
        app.get('/server-error-3', status=500)

    def test_server_error(self):
        app = TestApp(create_app(__name__))

        response = app.get('/server-error-1', status=500)
        self.assertIn('Test Exception', response.text)

        response = app.get('/server-error-2', status=500)
        self.assertIn("Renderer 'error' does not exist.", response.text)

        response = app.get('/server-error-3', status=500)
        self.assertIn('Renderer function has wrong args spec.', response.text)

    def test_server_error_debug(self):
        app = TestApp(create_app(debug=False, routes=ROUTES))
        response = app.get('/server-error-1', status=500)
        self.assertNotIn('Traceback', response.text)

        app = TestApp(create_app(debug=True, routes=ROUTES))
        response = app.get('/server-error-1', status=500)
        self.assertIn('Traceback', response.text)

    def test_static(self):
        app = TestApp(create_app(__name__))
        response = app.get('/static/{0}'.format(TEMPLATE_NAME), status=200)
        self.assertEqual(response.text, TEMPLATE)

    def test_static_routes(self):
        app = create_app(routes=ROUTES)
        routes = route(*ROUTES)
        self.assertNotEqual(len(routes.routes), len(app.routes.routes))

        app = create_app(debug=True, routes=ROUTES)
        self.assertNotEqual(len(routes.routes), len(app.routes.routes))

    def test_utils_absdir(self):
        self.assertEqual(absdir('user', '/Users'), '/Users/user')
        self.assertEqual(absdir('/Users/user', '/Users'), '/Users/user')

    def test_utils_force_unicode(self):
        u = str if six.PY3 else lambda value: unicode(value, 'utf-8')

        self.assertEqual(force_unicode('hello'), u('hello'))
        self.assertEqual(force_unicode('привет'), u('привет'))

        self.assertEqual(force_unicode(u('hello')), u('hello'))
        self.assertEqual(force_unicode(u('привет')), u('привет'))


def custom_command(app):
    print('Hello, world!')


def custom_json_renderer(data):
    return Response(json.dumps(data, indent=4),
                    content_type='application/json')


def custom_template_renderer(settings, renderer, data):
    return Response(Template('<h1>${var}</h1>').substitute(data))


def index_view():
    return 'Hello, world!'


def json_view():
    return {'var': 'Hello, world!'}


def server_error_view():
    raise Exception('Test Exception')


def template_view():
    return {'var': 'Hello, world!'}
