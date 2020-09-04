"""
==========
rororo.aio
==========

Various utilities for `aiohttp <https://aiohttp.rtfd.io/>`_ and other
`aio-libs <https://github.com/aio-libs>`_.

"""

from contextlib import contextmanager
from typing import Iterator, Optional, Union
from urllib.parse import urlparse

from aiohttp import web

from .annotations import DictStrAny, Handler, Protocol


__all__ = ("add_resource_context", "is_xhr_request", "parse_aioredis_url")


#: Default access log format to use within aiohttp applications
ACCESS_LOG_FORMAT = '%a "%r" %s %b "%{Referer}i" "%{User-Agent}i" %Tf'


class AddResourceFunc(Protocol):
    def __call__(
        self,
        url: str,
        get: Handler = None,
        *,
        name: str = None,
        **kwargs: Handler
    ) -> web.Resource:
        ...


@contextmanager
def add_resource_context(
    router: web.UrlDispatcher, url_prefix: str = None, name_prefix: str = None
) -> Iterator[AddResourceFunc]:
    """Context manager for adding resources for given router.

    Main goal of context manager to easify process of adding resources with
    routes to the router. This also allow to reduce amount of repeats, when
    supplying new resources by reusing URL & name prefixes for all routes
    inside context manager.

    Behind the scene, context manager returns a function which calls::

        resource = router.add_resource(url, name)
        resource.add_route(method, handler)

    For example to add index view handler and view handlers to list and create
    news::

        with add_resource_context(app.router, "/api", "api") as add_resource:
            add_resource("/", get=views.index)
            add_resource("/news", get=views.list_news, post=views.create_news)

    :param router: Route to add resources to.
    :param url_prefix: If supplied prepend this prefix to each resource URL.
    :param name_prefix: If supplied prepend this prefix to each resource name.
    """

    def add_resource(
        url: str, get: Handler = None, *, name: str = None, **kwargs: Handler
    ) -> web.Resource:
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
        """
        if get:
            kwargs["get"] = get

        if url_prefix:
            url = "/".join((url_prefix.rstrip("/"), url.lstrip("/")))

        if not name and get:
            name = get.__name__
        if name_prefix and name:
            name = ".".join((name_prefix.rstrip("."), name.lstrip(".")))

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
    value: Optional[str] = request.headers.get("X-Requested-With")
    return value == "XMLHttpRequest"


def parse_aioredis_url(url: str) -> DictStrAny:
    """
    Convert Redis URL string to dict suitable to pass to
    ``aioredis.create_redis(...)`` call.

    ::

        async def connect_redis(url=None):
            url = url or "redis://localhost:6379/0"
            return await create_redis(**parse_aioredis_url(url))

    :param url: URL to access Redis instance, started with ``redis://``.
    """
    parts = urlparse(url)

    db: Optional[Union[str, int]] = parts.path[1:] or None
    if db:
        db = int(db)

    return {
        "address": (parts.hostname, parts.port or 6379),
        "db": db,
        "password": parts.password,
    }
