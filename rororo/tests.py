# -*- coding: utf-8 -*-

import io
import json
import os
import sys
import tempfile

from string import Template

from jinja2.utils import escape
from webob.response import Response
from webtest import TestApp

from rororo import compat, exceptions
from rororo.app import create_app
from rororo.exceptions import ImproperlyConfigured, RouteReversalError
from rororo.manager import manage
from rororo.routes import GET, route
from rororo.utils import (
    absdir, dict_combine, force_unicode, inject_module, inject_settings,
    make_debug
)


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


class TestRororo(compat.TestCase):

    def setUp(self):
        if not os.path.isdir(STATIC_DIR):
            os.mkdir(STATIC_DIR)

        self.template = template = os.path.join(TEMPLATE_DIR, TEMPLATE_NAME)

        with open(template, 'w+') as handler:
            handler.write(TEMPLATE)

    def tearDown(self):
        if hasattr(self, 'old_argv'):
            sys.argv = self.old_argv

        if hasattr(self, 'old_stderr'):
            sys.stderr = self.old_stderr

    def test_create_app(self):
        app = create_app(__name__)
        self.assertTrue(callable(app), repr(app))

    def test_create_app_default_settings(self):
        app = create_app(routes=ROUTES)
        self.assertEqual(app.settings.APP_DIR, force_unicode(os.getcwd()))
        self.assertFalse(app.settings.DEBUG)
        self.assertFalse(app.settings.DISABLE_SETUP_LOGGING)
        self.assertFalse(app.settings.DISABLE_SETUP_TIMEZONE)
        self.assertEqual(app.settings.JINJA_GLOBALS, {})
        self.assertEqual(app.settings.JINJA_FILTERS, {})
        self.assertEqual(app.settings.JINJA_OPTIONS, {})
        self.assertIsNone(app.settings.LOCAL_LOGGING)
        self.assertEqual(app.settings.LOGGING, {})
        self.assertEqual(app.settings.PACKAGES, ())
        self.assertEqual(app.settings.PEP8_CLASS, 'pep8.StyleGuide')
        self.assertEqual(app.settings.PEP8_OPTIONS, {'statistics': True})
        self.assertEqual(app.settings.RENDERERS, ())
        self.assertEqual(app.settings.STATIC_DIR, 'static')
        self.assertEqual(app.settings.TEMPLATE_DIR, 'templates')
        self.assertEqual(app.settings.TIME_ZONE, os.environ.get('TZ'))
        self.assertFalse(app.settings.USE_PEP8)

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
        self.old_stderr = sys.stderr
        self.old_argv = sys.argv

        sys.argv = [sys.argv[0]]
        sys.stderr = io.StringIO() if compat.IS_PY3 else io.BytesIO()

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

    def test_redirect(self):
        app = create_app(__name__)
        response = app.redirect('json')
        self.assertEqual(response.code, 307)
        self.assertEqual(response.location, '/json')

        response = app.redirect('/')
        self.assertEqual(response.code, 307)
        self.assertEqual(response.location, '/')

    def test_redirect_permanent(self):
        app = create_app(__name__)
        response = app.redirect('json', _permanent=True)
        self.assertEqual(response.code, 301)
        self.assertEqual(response.location, '/json')

        response = app.redirect('/', _permanent=True)
        self.assertEqual(response.code, 301)
        self.assertEqual(response.location, '/')

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


class TestRororoUtils(compat.TestCase):

    def test_absdir(self):
        self.assertEqual(absdir('user', '/Users'), '/Users/user')
        self.assertEqual(absdir('/Users/user', '/Users'), '/Users/user')

    def test_dict_combine(self):
        self.assertEqual(dict_combine({}, {}), {})

        base = {'a': 1}
        extra = {'b': 2}
        combined = {'a': 1, 'b': 2}
        self.assertEqual(dict_combine(base, extra), combined)

        base['b'] = 3
        self.assertEqual(dict_combine(base, extra), combined)

        base['c'] = [1, 2]
        extra['c'] = 3
        self.assertRaises(AssertionError, dict_combine, base, extra)

        extra['c'] = [3]
        combined['c'] = [1, 2, 3]
        self.assertEqual(dict_combine(base, extra), combined)

        base['d'] = (1, 2)
        extra['d'] = 3
        self.assertRaises(AssertionError, dict_combine, base, extra)

        extra['d'] = (3, )
        combined['d'] = (1, 2, 3)
        self.assertEqual(dict_combine(base, extra), combined)

        base['e'] = set([1, 2])
        extra['e'] = 3
        self.assertRaises(AssertionError, dict_combine, base, extra)

        extra['e'] = set([3])
        combined['e'] = set([1, 2, 3])
        self.assertEqual(dict_combine(base, extra), combined)

        base['f'] = {'a': 1}
        extra['f'] = [2]
        self.assertRaises(AssertionError, dict_combine, base, extra)

        extra['f'] = {'b': 2}
        combined['f'] = {'a': 1, 'b': 2}
        self.assertEqual(dict_combine(base, extra), combined)

    def test_dict_combine_copy(self):
        base = {'a': 1}
        extra = {'b': 2}
        combined = {'a': 1, 'b': 2}

        self.assertEqual(dict_combine(base, extra, False), combined)
        self.assertEqual(base, combined)

    def test_force_unicode(self):
        self.assertEqual(force_unicode('hello'), compat.u('hello'))
        self.assertEqual(force_unicode('привет'), compat.u('привет'))

        self.assertEqual(force_unicode(compat.u('hello')), compat.u('hello'))
        self.assertEqual(force_unicode(compat.u('привет')), compat.u('привет'))

    def test_inject_module(self):
        data = {}
        self.assertTrue(inject_module(sys, data))
        self.assertEqual(data['path'], sys.path)

        data = {}
        self.assertTrue(inject_module('sys', data))
        self.assertEqual(data['path'], sys.path)

        data = {}
        self.assertRaises(ImportError, inject_module, 'does_not_exist', data)
        self.assertEqual(data, {})

    def test_inject_module_include_attr(self):
        data = {}
        inject_module('rororo.manager', data, include_attr='manage')
        self.assertIn('manage', data)
        self.assertIsNotNone(data['manage'])
        self.assertNotIn('DEFAULT_HOST', data)

        data = {}
        inject_module('rororo.manager', data, include_attr=set(['manage']))
        self.assertIn('manage', data)
        self.assertIsNotNone(data['manage'])
        self.assertNotIn('DEFAULT_HOST', data)

        data = {}
        func = lambda attr: attr.startswith('DEFAULT_')
        inject_module('rororo.manager', data, include_attr=func)
        self.assertNotIn('manage', data)
        self.assertIn('DEFAULT_HOST', data)

    def test_inject_module_include_value(self):
        data = {}
        inject_module('rororo.manager', data, include_value='0.0.0.0')
        self.assertIn('DEFAULT_HOST', data)
        self.assertNotIn('manage', data)

        data = {}
        inject_module('rororo.manager', data, include_value=[manage])
        self.assertIn('manage', data)
        self.assertNotIn('DEFAULT_HOST', data)

        data = {}
        func = lambda value: (isinstance(value, compat.string_types) and
                              value == '0.0.0.0')
        inject_module('rororo.manager', data, include_value=func)
        self.assertNotIn('manage', data)
        self.assertIn('DEFAULT_HOST', data)

    def test_inject_module_ignore_attr(self):
        data = {}
        inject_module('rororo.manager', data, ignore_attr='manage')
        self.assertNotIn('manage', data)
        self.assertIn('DEFAULT_HOST', data)

        data = {}
        inject_module('rororo.manager', data, ignore_attr=('manage', ))
        self.assertNotIn('manage', data)
        self.assertIn('DEFAULT_HOST', data)

        data = {}
        func = lambda attr: attr.startswith('DEFAULT_')
        inject_module('rororo.manager', data, ignore_attr=func)
        self.assertIn('manage', data)
        self.assertNotIn('DEFAULT_HOST', data)

    def test_inject_module_ignore_value(self):
        data = {}
        inject_module('rororo.manager', data, ignore_value='0.0.0.0')
        self.assertIn('manage', data)
        self.assertNotIn('DEFAULT_HOST', data)

        data = {}
        inject_module('rororo.manager', data, ignore_value=(manage, ))
        self.assertNotIn('manage', data)
        self.assertIn('DEFAULT_HOST', data)

        data = {}
        func = lambda value: (isinstance(value, compat.string_types) and
                              value == '0.0.0.0')
        inject_module('rororo.manager', data, ignore_value=func)
        self.assertIn('manage', data)
        self.assertNotIn('DEFAULT_HOST', data)

    def test_inject_module_overwrite(self):
        data = {}
        inject_module('rororo.manager', data)
        self.assertIsNotNone(data['manage'])

        data = {'manage': None}
        inject_module('rororo.manager', data, overwrite=None)
        self.assertIsNone(data['manage'])

    def test_inject_module_fail_silently(self):
        data = {}
        self.assertFalse(inject_module('rororo.does_not_exist',
                                       data,
                                       fail_silently=True))
        self.assertEqual(data, {})

    def test_inject_settings(self):
        data = {}
        inject_settings('rororo.manager', data)

        self.assertEqual(len(data), 2)
        self.assertIn('DEFAULT_HOST', data)
        self.assertIn('DEFAULT_PORT', data)
        self.assertNotIn('manage', data)
        old_data = data

        self.assertRaises(ImportError,
                          inject_settings,
                          'rororo.does_not_exist',
                          data)
        self.assertEqual(data, old_data)

    def test_inject_settings_overwrite(self):
        host = 'x.x.x.x'
        data = {'DEFAULT_HOST': host}
        inject_settings('rororo.manager', data)
        self.assertNotEqual(data['DEFAULT_HOST'], host)

        data = {'DEFAULT_HOST': host}
        inject_settings('rororo.manager', data, False)
        self.assertEqual(data['DEFAULT_HOST'], host)

    def test_inject_settings_fail_silently(self):
        data = {}
        inject_settings('rororo.does_not_exist', data, fail_silently=True)
        self.assertEqual(data, {})

    def test_make_debug(self):
        debug = make_debug()
        debug('Message', 'hidden')

    def test_make_debug_enabled(self):
        debug = make_debug(True)
        debug('Message', 'visible')

    def test_make_debug_extra(self):
        debug = make_debug(extra={'message_type': 'test'})
        debug('Message with type: {message_type}', 'hidden')


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
