"""
==================
rororo.annotations
==================

Internal module to keep all reusable type annotations for the project in one
place.

"""

import types
from typing import Any, Callable, Dict, Mapping, TypeVar, Union

try:
    from typing_extensions import Literal, Protocol, TypedDict
except ImportError:
    from typing import Literal, Protocol, TypedDict  # type: ignore

from aiohttp.web_middlewares import _Handler


Level = Literal["test", "dev", "staging", "prod"]

Handler = _Handler
Decorator = Callable[[Handler], Handler]

DictStrAny = Dict[str, Any]
DictStrInt = Dict[str, int]
DictStrStr = Dict[str, str]

MappingStrAny = Mapping[str, Any]
MappingStrInt = Mapping[str, int]
MappingStrStr = Mapping[str, str]

Settings = Union[types.ModuleType, DictStrAny]
T = TypeVar("T")


(Protocol, TypedDict)  # Make flake8 happy
