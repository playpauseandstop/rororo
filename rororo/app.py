"""
==========
rororo.app
==========

Create WSGI application from settings module and register all available
renderers.

"""

import copy
import os
import traceback

from jinja2 import Environment, FileSystemLoader
from routr import route
from routr.utils import import_string, inject_args
from webob.exc import no_escape
from webob.request import Request
from webob.response import Response

from .exceptions import (
    ImproperlyConfigured, HTTPException, HTTPServerError, NoMatchFound,
    NoRendererFound
)


DEFAULT_RENDERERS = (
    (lambda renderer: renderer is None, lambda _, data: Response(data)),
    ('json', lambda _, data: Response(json=data)),
    (
        lambda renderer: renderer.endswith(JINJA_HTML_TEMPLATES),
        lambda renderer, data: jinja_renderer(renderer, data)
    )
)
DEFAULT_SETTINGS = (
    ('APP_DIR', None),
    ('DEBUG', False),
    ('TEMPLATE_DIR', 'templates'),
)
JINJA_HTML_TEMPLATES = ('.htm', '.html', '.xhtml', '.xml')
RENDERERS = []
SETTINGS = {}


def config(key, value=None):
    """
    Read/write setting to local storage.
    """
    if value is None:
        return SETTINGS[key]
    SETTINGS[key] = value


def create_app(settings):
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
        routes = get_routes()

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

            # If response is not WebOb's instance - process it with available
            # renderers
            if not isinstance(response, Response):
                response = process_renderer(trace, response)
        # No route found in list of available ones
        except NoMatchFound as err:
            response = err.response
        # HTTP exception happened
        except HTTPException as err:
            response = err
        # Wrap any other exception to "Server Error"
        except Exception as err:
            message = traceback.format_exc() if config('DEBUG') else None
            response = HTTPServerError(message)

        # And finally return response to WSGI server
        return response(environ, start_response)

    # Populate settings with default ones
    global SETTINGS
    SETTINGS = dict(DEFAULT_SETTINGS)

    # Make able to load settings from pathes, not previously imported modules
    if isinstance(settings, basestring):
        settings = import_string(settings)

    # Only uppercased keys would be stored
    for attr in dir(settings):
        if attr.startswith('_') or not attr.isupper():
            continue
        SETTINGS[attr] = getattr(settings, attr)

    # If no specified ``APP_DIR`` used - set it to dir, where settings module
    # placed
    if not SETTINGS['APP_DIR']:
        SETTINGS['APP_DIR'] = \
            os.path.abspath(os.path.dirname(settings.__file__))

    # And finally do some validation, check that routes properly configured
    get_routes()

    # Return valid WSGI application
    return application


def get_routes():
    """
    Read routes from configuration and wrap it with ``routr.route`` function.
    """
    try:
        routes = config('ROUTES')
    except KeyError:
        raise ImproperlyConfigured('Please supply ROUTES setting. This '
                                   'setting is required.')
    return route(*routes)


def jinja_autoescape(filename):
    """
    Should we acitvate autoescaping for given filename or not.
    """
    if not filename:
        return False
    return filename.endswith(JINJA_HTML_TEMPLATES)


def jinja_env():
    """
    Prepare Jinja environment.
    """
    dirname = config('TEMPLATE_DIR')

    if not os.path.isabs(dirname):
        dirname = os.path.abspath(os.path.join(config('APP_DIR'), dirname))

    options = {'autfoescape': jinja_autoescape,
               'loader': FileSystemLoader(dirname)}
    env = Environment(**options)

    env.globals['config'] = config
    env.globals['reverse'] = get_routes().reverse

    return env


def jinja_renderer(filename, data):
    """
    Render template from ``filename`` using Jinja template engine.
    """
    template = jinja_env().get_template(filename)
    return Response(template.render(**data))


def match_renderer(key, renderer):
    """
    Returns True if ``key`` matches ``renderer``. ``key`` could be callable or
    static value.
    """
    return (callable(key) and key(renderer)) or \
           (not callable(key) and key == renderer)


def process_renderer(trace, data):
    """
    Extract ``renderer`` metadata from trace and run all available renderers to
    convert data to valid response.
    """
    renderer = trace.annotation('renderer')
    renderers = tuple(DEFAULT_RENDERERS) + tuple(RENDERERS)

    for key, func in renderers:
        if match_renderer(key, renderer):
           return func(renderer, data)

    raise NoRendererFound(renderer)


def renderer(key, func=None):
    """
    Read/write renderer to local storage.
    """
    if func is None:
        renderers = tuple(DEFAULT_RENDERERS) + tuple(RENDERERS)

        for added_key, added_func in renderers:
            if match_renderer(added_key, key):
                return added_func

        raise NoRendererFound(func)
    else:
        RENDERERS.append((key, func))
