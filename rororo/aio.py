"""
==========
rororo.aio
==========

Various utilities for aiohttp and other aio-libs.

"""

from contextlib import contextmanager
from typing import (  # noqa: F401
    Any,
    Callable,
    Dict,
    Iterator,
    Optional,
    TYPE_CHECKING,
    Union,
)
from urllib.parse import urlparse

# Hack to load ``aiohttp.web`` only on mypy run
if TYPE_CHECKING:  # pragma: no cover
    from aiohttp import web
else:
    web = type('FakeModule', (object, ), {
        'AbstractRouter': Any,
        'Request': Any,
        'Resource': Any,
        'Response': Any,
    })()


__all__ = ('add_resource_context', 'is_xhr_request', 'parse_aioredis_url')


View = Callable[[web.Request], web.Response]


@contextmanager
def add_resource_context(router: web.AbstractRouter,
                         url_prefix: str=None,
                         name_prefix: str=None) -> Iterator[Any]:
    """Context manager for adding resources for given router.

    Main goal of context manager to easify process of adding resources with
    routes to the router. This also allow to reduce amount of repeats, when
    supplying new resources by reusing URL & name prefixes for all routes
    inside context manager.

    Behind the scene, context manager returns a function which calls::

        resource = router.add_resource(url, name)
        resource.add_route(method, handler)

    **Usage**::

        with add_resource_context(app.router, '/api', 'api') as add_resource:
            add_resource('/', get=views.index)
            add_resource('/news', get=views.list_news, post=views.create_news)

    :param router: Route to add resources to.
    :param url_prefix: If supplied prepend this prefix to each resource URL.
    :param name_prefix: If supplied prepend this prefix to each resource name.
    """
    def add_resource(url: str,
                     get: View=None,
                     *,
                     name: str=None,
                     **kwargs: Any) -> web.Resource:
        """Inner function to create resource and add necessary routes to it.

        Support adding routes of all methods, supported by aiohttp, as
        GET/POST/PUT/PATCH/DELETE/HEAD/OPTIONS/*, e.g.,

        ::

            with add_resource_context(app.router) as add_resource:
                add_resource('/', get=views.get, post=views.post)
                add_resource('/wildcard', **{'*': views.wildcard})

        :param url:
            Resource URL. If ``url_prefix`` setup in context it will be
            prepended to URL with ``/``.
        :param get:
            GET handler. Only handler to be setup without explicit call.
        :param name: Resource name.
        :type name: str
        :rtype: aiohttp.web.Resource
        """
        kwargs['get'] = get

        if url_prefix:
            url = '/'.join((url_prefix.rstrip('/'), url.lstrip('/')))

        if not name and get:
            name = get.__name__
        if name_prefix and name:
            name = '.'.join((name_prefix.rstrip('.'), name.lstrip('.')))

        resource = router.add_resource(url, name=name)
        for method, handler in kwargs.items():
            if handler is None:
                continue
            resource.add_route(method.upper(), handler)

        return resource

    yield add_resource


def is_xhr_request(request: web.Request) -> bool:
    """Check whether current request is XHR one or not.

    Basically it just checks that request contains ``X-Requested-With`` header
    and that the header equals to ``XMLHttpRequest``.

    :param request: Request instance.
    """
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'


def parse_aioredis_url(url: str) -> Dict[str, Any]:
    """
    Convert Redis URL string to dict suitable to pass to
    ``aioredis.create_redis(...)`` call.

    **Usage**::

        async def connect_redis(url=None):
            url = url or 'redis://localhost:6379/0'
            return await create_redis(**get_aioredis_parts(url))

    :param url: URL to access Redis instance, started with ``redis://``.
    """
    parts = urlparse(url)

    db = parts.path[1:] or None  # type: Optional[Union[str, int]]
    if db:
        db = int(db)

    return {'address': (parts.hostname, parts.port or 6379),
            'db': db,
            'password': parts.password}
