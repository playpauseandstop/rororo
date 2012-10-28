import os
import uuid

from routr import GET, route
from routrschema import qs
from schemify import opt


def environ():
    return dict(os.environ)


def hello():
    return 'Hello, world!'


def page(pk):
    return 'Page #{0:d}'.format(int(pk))


def search(query=None):
    if not query:
        return 'Enter query to search'
    return 'Searching {0}...'.format(query)


def show_request(request, path):
    return {
        'headers': dict(request.headers),
        'method': request.method,
        'path': path,
    }


def template():
    return {'var': uuid.uuid4()}


routes = route('',
    GET('/', hello, name='hello'),
    GET('/environ', environ, name='environ', renderer='json'),
    GET('/page/{pk:int}', page, name='page'),
    GET('/search', qs(query=opt(str)), search, name='search'),
    GET('/request/{path:path}',
        show_request,
        name='show_request',
        renderer='json'),
    GET('/template', template, name='template', renderer='template.html'),
)
