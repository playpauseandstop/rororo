"""
==================
rororo.annotations
==================

Internal module to keep all reusable type annotations for the project in one
place.

"""

import types
from typing import Any, Callable, Dict, Mapping, TypeVar, Union

from aiohttp.web_middlewares import _Handler


Handler = _Handler
Decorator = Callable[[Handler], Handler]

DictStrAny = Dict[str, Any]
DictStrInt = Dict[str, int]
DictStrStr = Dict[str, str]

MappingStrAny = Mapping[str, Any]
MappingStrStr = Mapping[str, str]

Settings = Union[types.ModuleType, DictStrAny]
T = TypeVar("T")
