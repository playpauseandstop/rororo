import pytest
from aiohttp import web
from aiohttp.test_utils import make_mocked_request
from multidict import CIMultiDict

from rororo.aio import add_resource_context, is_xhr_request, parse_aioredis_url


async def dummy_handler(request):
    return web.Response(text="Hello, world!")


def check_length(iterable, expected):
    assert len(list(iterable)) == expected


def test_add_resource():
    router = web.UrlDispatcher()

    check_length(router.resources(), 0)
    check_length(router.routes(), 0)

    with add_resource_context(router) as add_resource:
        add_resource("/", dummy_handler, head=dummy_handler)

    check_length(router.resources(), 1)
    check_length(router.routes(), 2)


def test_add_resource_missed_handler():
    router = web.UrlDispatcher()

    with add_resource_context(router) as add_resource:
        add_resource("/", None, post=None)

    check_length(router.resources(), 1)
    check_length(router.routes(), 0)


def test_add_resource_name_prefix():
    router = web.UrlDispatcher()

    ctx = add_resource_context(router, name_prefix="prefix")
    with ctx as add_resource:
        add_resource("/", dummy_handler, name="index")

    assert str(router["prefix.index"].url_for()) == "/"


def test_add_resource_name_prefix_with_dot():
    router = web.UrlDispatcher()

    ctx = add_resource_context(router, name_prefix="with_dot.")
    with ctx as add_resource:
        add_resource("/with.dot", dummy_handler, name="index")

    assert str(router["with_dot.index"].url_for()) == "/with.dot"


def test_add_resource_real_world():
    router = web.UrlDispatcher()

    with add_resource_context(router, "/api/", "api") as add_resource:
        add_resource("/", dummy_handler, name="index")
        add_resource(
            "/news", get=dummy_handler, post=dummy_handler, name="news"
        )
        add_resource(
            r"/user/{user_id:\d+}",
            get=dummy_handler,
            patch=dummy_handler,
            put=dummy_handler,
            delete=dummy_handler,
            name="user",
        )

    check_length(router.resources(), 3)
    check_length(router.routes(), 7)

    assert str(router["api.index"].url_for()) == "/api/"
    assert str(router["api.news"].url_for()) == "/api/news"
    assert str(router["api.user"].url_for(user_id="1")) == "/api/user/1"


def test_add_resource_url_prefix():
    router = web.UrlDispatcher()

    ctx = add_resource_context(router, url_prefix="/api")
    with ctx as add_resource:
        add_resource("/", dummy_handler, name="index")
        add_resource(
            "/posts", get=dummy_handler, post=dummy_handler, name="posts"
        )

    check_length(router.resources(), 2)
    check_length(router.routes(), 3)

    assert str(router["index"].url_for()) == "/api/"
    assert str(router["posts"].url_for()) == "/api/posts"


def test_add_resource_url_prefix_with_slash():
    router = web.UrlDispatcher()

    ctx = add_resource_context(router, url_prefix="/api/")
    with ctx as add_resource:
        add_resource("/", dummy_handler, name="index")

    assert str(router["index"].url_for()) == "/api/"


def test_add_resource_wildcard():
    router = web.UrlDispatcher()

    with add_resource_context(router) as add_resource:
        add_resource("/", **{"*": dummy_handler})

    check_length(router.resources(), 1)
    check_length(router.routes(), 1)


def test_is_not_xhr_request():
    non_xhr_request = make_mocked_request("GET", "/")
    assert is_xhr_request(non_xhr_request) is False


def test_is_xhr_request():
    xhr_request = make_mocked_request(
        "GET",
        "/api/",
        headers=CIMultiDict({"X-Requested-With": "XMLHttpRequest"}),
    )
    assert is_xhr_request(xhr_request) is True


@pytest.mark.parametrize(
    "url, expected",
    (
        (
            "redis://localhost/",
            {"address": ("localhost", 6379), "db": None, "password": None},
        ),
        (
            "redis://127.0.0.1:6380/1",
            {"address": ("127.0.0.1", 6380), "db": 1, "password": None},
        ),
        (
            "redis://:pass@127.0.0.1:6379/",
            {"address": ("127.0.0.1", 6379), "db": None, "password": "pass"},
        ),
    ),
)
def test_parse_aioredis_url(url, expected):
    assert parse_aioredis_url(url) == expected
