"""
==========
rororo.app
==========

Create WSGI application and configure all necessary details.

Create application
==================

The main idea of ``rororo`` is an ability to fast construct and use WSGI apps
without Python OOP layer. And as ``rororo`` inspired from ``routr`` library
the next idea is reuse its routing system and made them a core of framework.

Routing
-------

You know, it maybe sounds very praised, but for me only necessary thing for
WSGI app is proper routing layer for connect requested path info with necessary
view function.

And next big question, are we really everytime need to pass ``request``
instance to our view functions? Sometime this is very big limitation and
sometime this limitation walks our views away from all other buisness logic.

Process renderers
=================

Custom renderers
----------------

Available settings
==================

APP_DIR
-------

Application directory. Needed if static or template directory has relative not
absolute path, then rel path joined with app directory to result.

By default: directory where settings module located or current working
directory.

DEBUG
-----

Debug mode. Main core feature of debug mode is support static files by adding
static route to list of all application routes.

By default: ``False``

DISABLE_SETUP_LOGGING
---------------------

Disable auto setup logging from ``LOGGING`` and ``LOCAL_LOGGING`` dict configs.

By default: ``False``

DISABLE_SETUP_TIMEZONE
----------------------

Disable setup timezone from ``TIME_ZONE`` settings.

By default: ``False``

JINJA_FILTERS
-------------

Dictionary with filters to use in Jinja templates.

By default: ``{}``

JINJA_GLOBALS
-------------

Dictionary with globals which send to each Jinja template.

By default: ``{}``

JINJA_OPTIONS
-------------

Options to initialize Jinja2 environment.

By default: ``{}``

LOCAL_LOGGING
-------------

Local logging settings to customize original (base) logging settings.

By default: ``None``

LOGGING
-------

Base logging settings which later would be passed to
``logging.config.dictConfig`` method.

By default: ``{}``

PACKAGES
--------

Sequence with all additional packages which would be installed to current app.

Package is just a Python package compatible with rororo, same as reusable app
is for Django project or Flask blueprint is for Flask app.

Main reason of adding package to application is adding additional views,
templates and static directories to application.

.. important:: Right now it is concept and not a final solution.

By default: ``()``

PEP8_CLASS
----------

Path to PEP8 style guide class.

By default: ``pep8.StyleGuide``

PEP8_OPTIONS
------------

Keyword arguments passed to PEP8 style guide class on initialization when
checking PEP8 for current app and all its packages.

By default: ``{'statistics': True}``

RENDERERS
---------

Sequence with all custom renderers in format ``(test, func)``.

By default: ``()``

ROUTES
------

**Required**. All available routes for your app in list or tuple format. These
routes would be wrapped with ``routr.route`` function.

ROUTES_VIEW_PREFIX
------------------

Prepend text to each view string which contains in ``ROUTES`` list.

By default: ``None``

STATIC_DIR
----------

Directory where static files placed. Necessary only for debug mode and
easyfying static files support. If value is relpath it would be joined with app
directory.

By default: ``'static'``

STATIC_URL
----------

URL for static files route. Used only in debug mode.

If you want to have static files handling by WebOb in any mode - just add::

    static(STATIC_URL, STATIC_DIR, name='static')

route to list of all ``ROUTES``.

By default: ``'/static'``

TEMPLATE_DIR
------------

Directory with Jinja templates. If value is relpath it would be joined with app
directory.

By default: ``'templates'``

TIME_ZONE
---------

Standart UNIX timezone to use in application.

By default: ``os.environ.get('TZ')``

"""

import copy
import inspect
import operator
import os
import traceback

from jinja2 import Environment, FileSystemLoader
from routr import Endpoint, route
from routr.exc import RouteReversalError
from routr.utils import import_string, inject_args
from webob.exc import HTTPMovedPermanently, HTTPFound
from webob.request import Request
from webob.response import Response

from . import compat

from .exceptions import (
    ImproperlyConfigured, HTTPException, HTTPServerError, NoMatchFound,
    NoRendererFound
)
from .static import static
from .utils import absdir, force_unicode, setup_logging, setup_timezone


DEFAULT_RENDERERS = (
    ('json', lambda data: Response(json=data)),
    ('text', lambda data: Response(data, content_type='text/plain')),
    (lambda renderer: renderer is None, lambda data: Response(data)),
    (
        lambda renderer: renderer.endswith(JINJA_HTML_TEMPLATES),
        lambda settings, renderer, data: jinja_renderer(
            settings, renderer, data
        )
    )
)
DEFAULT_SETTINGS = (
    ('APP_DIR', None),
    ('DEBUG', False),
    ('DISABLE_SETUP_LOGGING', False),
    ('DISABLE_SETUP_TIMEZONE', False),
    ('JINJA_FILTERS', {}),
    ('JINJA_GLOBALS', {}),
    ('JINJA_OPTIONS', {}),
    ('LOCAL_LOGGING', None),
    ('LOGGING', {}),
    ('PACKAGES', ()),
    ('PEP8_CLASS', 'pep8.StyleGuide'),
    ('PEP8_OPTIONS', {'statistics': True}),
    ('RENDERERS', ()),
    ('ROUTES_VIEW_PREFIX', None),
    ('STATIC_DIR', 'static'),
    ('STATIC_URL', '/static'),
    ('TEMPLATE_DIR', 'templates'),
    ('TIME_ZONE', os.environ.get('TZ')),
    ('USE_PEP8', False),
)
JINJA_HTML_TEMPLATES = ('.htm', '.html', '.xhtml', '.xml')


class Rororo(object):
    """
    Simple class which gives ability to wrap original WSGI application in
    WSGI middlewares.
    """
    __slots__ = ('packages', 'routes', 'settings', 'wsgi_app')

    def __init__(self, application, settings, packages, routes):
        """
        Initialize WSGI-compatible app with extra info.
        """
        self.packages = packages
        self.routes = routes
        self.settings = settings
        self.wsgi_app = application

    def __call__(self, environ, start_response):
        """
        Shortcut for ``wsgi_app``.
        """
        return self.wsgi_app(environ, start_response)

    def redirect(self, location, *args, **kwargs):
        """
        Shortcut for making redirects.
        """
        permanent = kwargs.pop('_permanent', False)
        klass = HTTPMovedPermanently if permanent else HTTPFound

        try:
            return klass(location=self.reverse(location, *args, **kwargs))
        except RouteReversalError:
            return klass(location=location, *args, **kwargs)

    def reverse(self, *args, **kwargs):
        """
        Shortcut for reversing routes.
        """
        return self.routes.reverse(*args, **kwargs)


def create_app(mixed=None, **kwargs):
    """
    Load settings from Python module and return valid WSGI application.

    Settings should contain ``ROUTES`` var, else ``ImproperlyConfigured`` error
    would be raised.

    ``ROUTES`` should be a ``tuple`` which would be wrapped with
    ``routr.route`` function.
    """
    def application(environ, start_response):
        """
        WSGI application. Place where all routr handling done.
        """
        # Initialize request, based on current environ
        request = Request(environ)

        # Read routes from current config and initialize them
        routes = get_routes(settings)

        # Start routing
        try:
            # Trace all available routes to find view to execute
            trace = routes(request)
            view = trace.target

            # If target is string - try to import function from its notation
            if isinstance(view, compat.string_types):
                prefix = settings.ROUTES_VIEW_PREFIX

                if prefix:
                    view = '.'.join((prefix, view))

                view = import_string(view)

            # Inject request into view args if necessary
            args, kwargs = trace.args, trace.kwargs
            args = inject_args(view, args, request=request)

            # Run view function
            response = view(*args, **kwargs)

            # If response is not WebOb's instance - process it with all
            # available renderers
            if not isinstance(response, Response):
                renderer = trace.annotation('renderer')
                response = process_renderer(settings, renderer, response)
        # Process exceptions
        except Exception as err:
            # No route found in list of available ones
            if isinstance(err, NoMatchFound):
                response = err.response
            # HTTP exception happened
            elif isinstance(err, HTTPException):
                response = err
            # Wrap any other exception to "Server Error"
            else:
                message = traceback.format_exc() if settings.DEBUG else None
                response = HTTPServerError(message)

        # And finally return response to WSGI server
        return response(environ, start_response)

    # Load default setttings from predefined values
    settings = type('Settings', (object, ), dict(DEFAULT_SETTINGS))()

    # Make able to load settings from pathes, not only from previously imported
    # modules
    if mixed:
        all_settings = (import_string(mixed)
                        if isinstance(mixed, compat.string_types)
                        else mixed)
    # But also have ability to load settings from keyword arguments to easify
    # creating applications for testing
    else:
        all_settings = None
        kwargs = dict(zip(
            map(operator.methodcaller('upper'), kwargs.keys()),
            kwargs.values()
        ))
        settings.__dict__.update(kwargs)

    # Only uppercased keys would be stored
    for attr in dir(all_settings):
        if attr.startswith('_') or not attr.isupper():
            continue
        setattr(settings, attr, getattr(all_settings, attr))

    # If ``APP_DIR`` not specified - set it to dir, where settings module
    # placed or current work directory
    if not settings.APP_DIR:
        if hasattr(all_settings, '__file__'):
            dirname = os.path.abspath(os.path.dirname(all_settings.__file__))
        else:
            dirname = os.getcwdu() if not compat.IS_PY3 else os.getcwd()

        settings.APP_DIR = dirname

    # Path should be an unicode
    settings.APP_DIR = force_unicode(settings.APP_DIR)

    # Setup initial template and static directories sequences
    settings._PACKAGE_DIRS = []
    settings._STATIC_DIRS = [absdir(settings.STATIC_DIR, settings.APP_DIR)]
    settings._TEMPLATE_DIRS = [absdir(settings.TEMPLATE_DIR, settings.APP_DIR)]

    # Also setup logging and timezone for application
    if not settings.DISABLE_SETUP_LOGGING:
        setup_logging(settings.LOGGING, settings.LOCAL_LOGGING)

    if not settings.DISABLE_SETUP_TIMEZONE:
        setup_timezone(settings.TIME_ZONE)

    # Now it's time to load all packages if any and modify settings a bit if
    # necessary (settings.PACKAGES is not an empty sequence)
    packages = register_packages(settings)

    # And finally do some validation, check that routes properly configured and
    # if yes save them in application as well as settings
    routes = get_routes(settings)

    # Make and return suitable WSGI application
    return Rororo(application, settings, packages, routes)


def get_routes(settings):
    """
    Read routes from configuration and wrap it with ``routr.route`` function.
    """
    # Settings should contain ``ROUTES``
    try:
        routes = settings.ROUTES
    except AttributeError:
        raise ImproperlyConfigured('Please supply ROUTES setting. This '
                                   'setting is required.')

    # Routes should be a list or a tuple
    if not isinstance(routes, (list, tuple)):
        raise ImproperlyConfigured('ROUTES should be a list or tuple.')

    # Add static view to routes if possible
    if settings.STATIC_URL and settings.STATIC_URL.startswith('/'):
        routes = list(routes)
        routes.insert(
            1 if isinstance(routes[0], compat.string_types) else 0,
            static(settings.STATIC_URL, settings._STATIC_DIRS, name='static')
        )

    # Loop over all possible routes and add default name when necessary
    unique = set()

    for item in routes:
        # Avoid route groups
        if isinstance(item, compat.string_types):
            continue

        # Remember all already defined route names
        if item.name:
            unique.add(item.name)
            continue

        # Calculate new route name
        name = (compat.func_name(item.target)
                if callable(item.target)
                else item.target.rsplit('.', 1)[-1])

        # Route name should be unique, it means it applied only for first route
        # of multiple defined views
        if name not in unique:
            unique.add(name)
            item.name = name

    # And finally initialize routes with wrapping to ``route`` function
    return route(*routes)


def jinja_autoescape(filename):
    """
    Should we acitvate autoescaping for given filename or not.
    """
    if not filename:
        return False
    return filename.endswith(JINJA_HTML_TEMPLATES)


def jinja_env(settings):
    """
    Prepare Jinja environment.
    """
    # Prepare Jinja options
    options = copy.deepcopy(settings.JINJA_OPTIONS)
    options.setdefault('autoescape', jinja_autoescape)
    options.setdefault('loader', FileSystemLoader(settings._TEMPLATE_DIRS))

    # And make Jinja environment
    env = Environment(**options)

    # Populate all filters and globals from settings
    for key, value in compat.iteritems(settings.JINJA_FILTERS):
        env.filters[key] = value

    for key, value in compat.iteritems(settings.JINJA_GLOBALS):
        env.globals[key] = value

    # Remove ability of overwriting reverse and settings globals
    env.globals['reverse'] = get_routes(settings).reverse
    env.globals['settings'] = settings

    return env


def jinja_renderer(settings, filename, data):
    """
    Render template from ``filename`` using Jinja template engine.
    """
    if not isinstance(data, dict):
        raise ValueError('Unable to render template without proper context. '
                         'Passed context: {0!r}'.format(data))

    template = jinja_env(settings).get_template(filename)
    return Response(template.render(**data))


def match_renderer(key, renderer):
    """
    Returns True if ``key`` matches ``renderer``. ``key`` could be callable or
    static value.
    """
    return (callable(key) and key(renderer)) or \
           (not callable(key) and key == renderer)


def process_renderer(settings, renderer, data):
    """
    Extract ``renderer`` metadata from trace and run all available renderers to
    convert data to valid response.
    """
    renderers = tuple(DEFAULT_RENDERERS) + tuple(settings.RENDERERS)

    for key, mixed in renderers:
        if match_renderer(key, renderer):
            is_class = False

            if isinstance(mixed, compat.string_types):
                func = import_string(mixed)
            elif inspect.isclass(mixed):
                func = mixed.__init__
                is_class = True
            else:
                func = mixed

            args_count = len(inspect.getargspec(func).args or ())
            args_count = args_count - 1 if is_class else args_count
            func = mixed if is_class else func

            if args_count == 1:
                return func(data)
            elif args_count == 3:
                return func(settings, renderer, data)
            else:
                raise ValueError('Renderer function has wrong args spec.')

    raise NoRendererFound(renderer)


def register_packages(settings):
    """
    If ``settings.PACKAGES`` is not an empty list/tuple - extend routes,
    template and static directories and jinja globals/filters from package
    settings if any.
    """
    def append_settings(settings, package_settings, package_name, package_dir):
        """
        Append routes, template and static directories to global settings.
        """
        if not isinstance(settings.ROUTES, list):
            settings.ROUTES = list(settings.ROUTES)

        static_dir = getattr(package_settings,
                             'STATIC_DIR',
                             default_settings['STATIC_DIR'])

        template_dir = getattr(package_settings,
                               'TEMPLATE_DIR',
                               default_settings['TEMPLATE_DIR'])

        settings._STATIC_DIRS.append(absdir(static_dir, package_dir))
        settings._TEMPLATE_DIRS.append(absdir(template_dir, package_dir))

        if hasattr(package_settings, 'JINJA_GLOBALS'):
            settings.JINJA_GLOBALS.update(package_settings.JINJA_GLOBALS)

        if hasattr(package_settings, 'JINJA_FILTERS'):
            settings.JINJA_FILTERS.update(package_settings.JINJA_FILTERS)

        if hasattr(package_settings, 'ROUTES'):
            settings.ROUTES.extend(
                safe_include(package_settings.ROUTES, package_name)
            )

    def safe_include(routes, package_name):
        """
        Safe include of routes from packages by wrapping them to route.
        """
        routes = list(routes)
        base_pattern = routes.pop(0)

        if isinstance(base_pattern, compat.string_types):
            base_pattern = base_pattern.rstrip('/')
        else:
            routes.insert(0, base_pattern)
            base_pattern = None

        for endpoint in routes:
            if isinstance(endpoint, Endpoint) and endpoint.name:
                endpoint.name = ':'.join((package_name, endpoint.name))

                if base_pattern:
                    endpoint.pattern.pattern = (
                        ''.join((base_pattern, endpoint.pattern.pattern))
                    )

        return tuple(routes)

    # Initial vars
    default_settings = dict(DEFAULT_SETTINGS)
    packages = []

    # For each package, try to load it and load its settings
    for package_name in settings.PACKAGES:
        package = import_string(package_name)
        package_dir = force_unicode(
            os.path.abspath(os.path.dirname(package.__file__))
        )

        # Package could be without settings too. This just means that we don't
        # need to do any modifications with current settings
        package_settings_module = '{0}.settings'.format(package_name)

        try:
            package_settings = import_string(package_settings_module)
        except ImportError:
            pass
        else:
            args = (settings, package_settings, package_name, package_dir)
            append_settings(*args)

        settings._PACKAGE_DIRS.append(package_dir)
        packages.append(package_name)

    return tuple(packages)
