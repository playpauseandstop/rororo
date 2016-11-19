import asyncio

from unittest import TestCase

from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase, make_mocked_request
from multidict import CIMultiDict

from rororo.aio import add_resource_context, parse_aioredis_url, is_xhr_request


@asyncio.coroutine
def dummy_handler(request):
    return web.Response(text='Hello, world!')


class TestAddResourceContext(AioHTTPTestCase):

    def check_length(self, iterable, expected):
        self.assertEqual(len(list(iterable)), expected)

    def get_app(self, loop):
        return web.Application(loop=loop)

    def test_add_resource(self):
        router = web.UrlDispatcher(self.app)

        self.check_length(router.resources(), 0)
        self.check_length(router.routes(), 0)

        with add_resource_context(router) as add_resource:
            add_resource('/', dummy_handler, head=dummy_handler)

        self.check_length(router.resources(), 1)
        self.check_length(router.routes(), 2)

    def test_add_resource_missed_handler(self):
        router = web.UrlDispatcher(self.app)

        with add_resource_context(router) as add_resource:
            add_resource('/', None, post=None)

        self.check_length(router.resources(), 1)
        self.check_length(router.routes(), 0)

    def test_add_resource_name_prefix(self):
        router = web.UrlDispatcher(self.app)

        ctx = add_resource_context(router, name_prefix='prefix')
        with ctx as add_resource:
            add_resource('/', dummy_handler, name='index')

        self.assertEqual(router['prefix.index'].url(), '/')

    def test_add_resource_name_prefix_with_dot(self):
        router = web.UrlDispatcher(self.app)

        ctx = add_resource_context(router, name_prefix='with_dot.')
        with ctx as add_resource:
            add_resource('/with.dot', dummy_handler, name='index')

        self.assertEqual(router['with_dot.index'].url(), '/with.dot')

    def test_add_resource_real_world(self):
        router = web.UrlDispatcher(self.app)

        with add_resource_context(router, '/api/', 'api') as add_resource:
            add_resource('/', dummy_handler, name='index')
            add_resource('/news',
                         get=dummy_handler,
                         post=dummy_handler,
                         name='news')
            add_resource('/user/{user_id:\d+}',
                         get=dummy_handler,
                         patch=dummy_handler,
                         put=dummy_handler,
                         delete=dummy_handler,
                         name='user')

        self.check_length(router.resources(), 3)
        self.check_length(router.routes(), 7)

        self.assertEqual(router['api.index'].url(), '/api/')
        self.assertEqual(router['api.news'].url(), '/api/news')
        self.assertEqual(router['api.user'].url(parts={'user_id': 1}),
                         '/api/user/1')

    def test_add_resource_url_prefix(self):
        router = web.UrlDispatcher(self.app)

        ctx = add_resource_context(router, url_prefix='/api')
        with ctx as add_resource:
            add_resource('/', dummy_handler, name='index')
            add_resource('/posts',
                         get=dummy_handler,
                         post=dummy_handler,
                         name='posts')

        self.check_length(router.resources(), 2)
        self.check_length(router.routes(), 3)

        self.assertEqual(router['index'].url(), '/api/')
        self.assertEqual(router['posts'].url(), '/api/posts')

    def test_add_resource_url_prefix_with_slash(self):
        router = web.UrlDispatcher(self.app)

        ctx = add_resource_context(router, url_prefix='/api/')
        with ctx as add_resource:
            add_resource('/', dummy_handler, name='index')

        self.assertEqual(router['index'].url(), '/api/')

    def test_add_resource_wildcard(self):
        router = web.UrlDispatcher(self.app)

        with add_resource_context(router) as add_resource:
            add_resource('/', **{'*': dummy_handler})

        self.check_length(router.resources(), 1)
        self.check_length(router.routes(), 1)


class TestAioUtils(TestCase):

    def test_is_xhr_request(self):
        non_xhr_request = make_mocked_request('GET', '/')
        self.assertFalse(is_xhr_request(non_xhr_request))

        xhr_request = make_mocked_request('GET', '/api/', headers=CIMultiDict({
            'X-Requested-With': 'XMLHttpRequest',
        }))
        self.assertTrue(is_xhr_request(xhr_request))

    def test_parse_aioredis_url(self):
        self.assertEqual(
            parse_aioredis_url('redis://localhost/'),
            {'address': ('localhost', 6379), 'db': None, 'password': None})

        self.assertEqual(
            parse_aioredis_url('redis://127.0.0.1:6380/1'),
            {'address': ('127.0.0.1', 6380), 'db': 1, 'password': None})

        self.assertEqual(
            parse_aioredis_url('redis://:pass@127.0.0.1:6379/'),
            {'address': ('127.0.0.1', 6379), 'db': None, 'password': 'pass'})
