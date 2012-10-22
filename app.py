import os

from jinja2 import Environment, PackageLoader
from routr import include, route
from routr.exc import NoMatchFound
from routr.utils import inject_args
from webob.exc import HTTPException
from webob.request import Request
from webob.response import Response
from wsgiref.simple_server import make_server

from views import routes


routes = route('',
    include('views:routes'),
)


def application(environ, start_response):
    """
    Main WSGI application.
    """
    request = Request(environ)

    try:
        trace = routes(request)
        view = trace.target

        args, kwargs = trace.args, trace.kwargs
        args = inject_args(view, args, request=request)

        response = view(*args, **kwargs)
        if not isinstance(response, Response):
            response = process_renderer(trace, response)
    except NoMatchFound, e:
        response = e.response
    except HTTPException, e:
        response = e

    return response(environ, start_response)


def process_renderer(trace, data):
    """
    Extract renderer metadata from ``trace`` and apply specified renderer to
    ``data``.
    """
    renderer = trace.endpoint.annotations.get('renderer')

    if renderer is None:
        return Response(data)
    elif renderer == 'json':
        return Response(json=data)
    elif renderer.endswith('.html'):
        env = Environment(loader=PackageLoader('app', 'templates'))
        env.globals['reverse'] = routes.reverse
        template = env.get_template(renderer)
        return Response(template.render(**data))

    raise ValueError('Unknown renderer {0!r}'.format(renderer))

if __name__ == '__main__':
    server = make_server(
        os.environ.get('HOST', '0.0.0.0'),
        int(os.environ.get('PORT', 8080)),
        application
    )

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('^C')
