import json
import os
import uuid

from jinja2 import Environment, PackageLoader
from routr import GET, POST, route
from routr.exc import NoMatchFound
from routr.utils import import_string
from routrschema import qs
from schemify import opt
from webob.exc import HTTPException
from webob.request import Request
from webob.response import Response
from wsgiref.simple_server import make_server


def environ():
    response = Response(json.dumps(dict(os.environ)))
    response.headers['Content-Type'] = 'application/json'
    return response


def hello():
    return Response('Hello, world!')


def page(pk):
    return Response('Page #{}!'.format(int(pk)))


def search(query=None):
    if not query:
        return Response('Enter query to search')
    return Response('Searching {}...'.format(query))


def template_view():
    template = env.get_template('template.html')
    return Response(template.render(var=uuid.uuid4()))


routes = route('',
    route(GET, '/', hello, name='hello'),
    route(GET, '/environ', environ, name='environ'),
    route(GET, '/page/{pk:int}', page, name='page'),
    route(GET, '/search', qs(query=opt(str)), search, name='search'),
    route(GET, '/template', template_view, name='template'),
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
    except NoMatchFound, e:
        response = e.response
    except HTTPException, e:
        response = e
    return response(environ, start_response)


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
