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
    from typing import Literal, Protocol, TypedDict
except ImportError:
    from typing_extensions import Literal, Protocol, TypedDict  # type: ignore[misc]

from aiohttp import web
from aiohttp_middlewares.annotations import Handler


F = TypeVar("F", bound=Callable[..., Any])  # noqa: VNE001
T = TypeVar("T")

Level = Literal["test", "dev", "staging", "prod"]

ViewType = Type[web.View]

DictStrAny = Dict[str, Any]
DictStrInt = Dict[str, int]
DictStrStr = Dict[str, str]

MappingStrAny = Mapping[str, Any]
MappingStrInt = Mapping[str, int]
MappingStrStr = Mapping[str, str]

Settings = Union[types.ModuleType, DictStrAny]


(Handler, Protocol, TypedDict)  # Make flake8 happy
