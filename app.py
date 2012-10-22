import json
import os
import uuid

from jinja2 import Environment, PackageLoader
from routr import GET, POST, route
from routr.exc import NoMatchFound
from routrschema import qs
from schemify import opt
from webob.exc import HTTPException
from webob.request import Request
from webob.response import Response
from wsgiref.simple_server import make_server


def environ():
    return dict(os.environ)

def hello():
    return 'Hello, world!'

def page(pk):
    return 'Page #{}!'.format(int(pk))

def search(query=None):
    if not query:
        return 'Enter query to search'
    return 'Searching {}...'.format(query)

def template_view():
    return {'var': uuid.uuid4()}

routes = route(
    GET('/', hello, name='hello'),
    GET('/environ', environ, name='environ', renderer='json'),
    GET('/page/{pk:int}', page, name='page'),
    GET('/search', qs(query=opt(str)), search, name='search'),
    GET('/template', template_view, name='template', renderer='template.html'),
)

env = Environment(loader=PackageLoader('app', 'templates'))
env.globals['reverse'] = routes.reverse


def application(environ, start_response):
    request = Request(environ)

    try:
        trace = routes(request)
        view = trace.target
        args, kwargs = trace.args, trace.kwargs
        response = view(*args, **kwargs)
        if not isinstance(response, Response):
            response = process_renderer(trace, response)
    except NoMatchFound, e:
        response = e.response
    except HTTPException, e:
        response = e
    return response(environ, start_response)

def process_renderer(trace, data):
    """ Extract renderer metadata from ``trace`` and apply specified renderer to
    ``data``"""
    renderer = trace.endpoint.annotations.get('renderer')
    if renderer is None:
        return Response(data)
    elif renderer == 'json':
        return Response(json=data)
    elif renderer.endswith('.html'):
        template = env.get_template(renderer)
        return Response(template.render(**data))
    else:
        raise ValueError('unknown renderer %s' % renderer)

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
