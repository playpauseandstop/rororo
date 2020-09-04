"""
==================
rororo.annotations
==================

Internal module to keep all reusable type annotations for the project in one
place.

"""

import types
from typing import Any, Callable, Dict, Mapping, Type, TypeVar, Union

try:
    from typing_extensions import Literal, Protocol, TypedDict
except ImportError:
    from typing import Literal, Protocol, TypedDict  # type: ignore

from aiohttp import web
from aiohttp.web_middlewares import _Handler


F = TypeVar("F", bound=Callable[..., Any])  # noqa: VNE001
T = TypeVar("T")

Level = Literal["test", "dev", "staging", "prod"]

Handler = _Handler
ViewType = Type[web.View]

DictStrAny = Dict[str, Any]
DictStrInt = Dict[str, int]
DictStrStr = Dict[str, str]

MappingStrAny = Mapping[str, Any]
MappingStrInt = Mapping[str, int]
MappingStrStr = Mapping[str, str]

Settings = Union[types.ModuleType, DictStrAny]


(Protocol, TypedDict)  # Make flake8 happy
