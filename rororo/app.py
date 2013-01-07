"""
==========
rororo.app
==========

Create WSGI application from settings module and register all available
renderers.

"""

import copy
import inspect
import operator
import os
import traceback

from jinja2 import Environment, FileSystemLoader
from routr import route
from routr.static import static
from routr.utils import import_string, inject_args
from webob.exc import no_escape
from webob.request import Request
from webob.response import Response

from .exceptions import (
    ImproperlyConfigured, HTTPException, HTTPServerError, NoMatchFound,
    NoRendererFound
)


DEFAULT_RENDERERS = (
    ('json', lambda data: Response(json=data)),
    ('text', lambda data: Response(data, content_type='text/plain')),
    (lambda renderer: renderer is None, lambda data: Response(data)),
    (
        lambda renderer: renderer.endswith(JINJA_HTML_TEMPLATES),
        lambda settings, renderer, data: \
            jinja_renderer(settings, renderer, data)
    )
)
DEFAULT_SETTINGS = (
    ('APP_DIR', None),
    ('DEBUG', False),
    ('JINJA_OPTIONS', {}),
    ('RENDERERS', ()),
    ('STATIC_DIR', 'static'),
    ('STATIC_URL', '/static'),
    ('TEMPLATE_DIR', 'templates'),
)
JINJA_HTML_TEMPLATES = ('.htm', '.html', '.xhtml', '.xml')


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
            view = import_string(view) \
                   if isinstance(view, basestring) \
                   else view

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
        # No route found in list of available ones
        except NoMatchFound as err:
            response = err.response
        # HTTP exception happened
        except HTTPException as err:
            response = err
        # Wrap any other exception to "Server Error"
        except Exception as err:
            message = traceback.format_exc() if settings.DEBUG else None
            response = HTTPServerError(message)

        # And finally return response to WSGI server
        return response(environ, start_response)

    # Load default setttings from predefined values
    settings = type('Settings', (object, ), dict(DEFAULT_SETTINGS))()

    # Make able to load settings from pathes, not only from previously imported
    # modules
    if mixed:
        all_settings = import_string(mixed) \
                       if isinstance(mixed, basestring) \
                       else mixed
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
            dirname = os.getcwdu()

        # Path should be an unicode
        if not isinstance(dirname, unicode):
            dirname = dirname.decode('utf-8')

        settings.APP_DIR = dirname

    # And finally do some validation, check that routes properly configured and
    # if yes save them in application as well as settings
    routes = get_routes(settings)

    setattr(application, 'routes', routes)
    setattr(application, 'settings', settings)

    # Return valid WSGI application
    return application


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

    # Add static view to routes, but only in debug mode
    if settings.DEBUG:
        dirname = settings.STATIC_DIR
        routes = list(routes)

        if not os.path.isabs(dirname):
            dirname = os.path.abspath(os.path.join(settings.APP_DIR, dirname))

        index = 1 if isinstance(routes[0], basestring) else 0
        routes.insert(
            index, static(settings.STATIC_URL, dirname, name='static')
        )

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
    dirname = settings.TEMPLATE_DIR

    if not os.path.isabs(dirname):
        dirname = os.path.abspath(os.path.join(settings.APP_DIR, dirname))

    options = copy.deepcopy(settings.JINJA_OPTIONS)
    options.setdefault('autoescape', jinja_autoescape)
    options.setdefault('loader', FileSystemLoader(dirname))

    env = Environment(**options)

    env.globals['reverse'] = get_routes(settings).reverse
    env.globals['settings'] = settings

    return env


def jinja_renderer(settings, filename, data):
    """
    Render template from ``filename`` using Jinja template engine.
    """
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

            if isinstance(mixed, basestring):
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
