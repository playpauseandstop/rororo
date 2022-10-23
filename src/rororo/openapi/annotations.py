from typing import Any, Dict, List, Tuple, Union

from aiohttp_middlewares.annotations import (
    ExceptionType,
    Handler,
    StrCollection,
    UrlCollection,
)
from aiohttp_middlewares.error import Config as ErrorMiddlewareConfig

from rororo.annotations import TypedDict


SecurityDict = Dict[str, List[str]]


class CorsMiddlewareKwargsDict(TypedDict, total=False):
    allow_all: bool
    origins: Union[UrlCollection, None]
    urls: Union[UrlCollection, None]
    expose_headers: Union[StrCollection, None]
    allow_headers: StrCollection
    allow_methods: StrCollection
    allow_credentials: bool
    max_age: Union[int, None]


class ErrorMiddlewareKwargsDict(TypedDict, total=False):
    default_handler: Handler
    config: Union[ErrorMiddlewareConfig, None]
    ignore_exceptions: Union[ExceptionType, Tuple[ExceptionType, ...], None]


class ValidateEmailKwargsDict(TypedDict, total=False):
    allow_smtputf8: bool
    allow_empty_local: bool
    check_deliverability: bool
    timeout: Union[int, float]
    dns_resolver: Any
