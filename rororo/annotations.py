"""
==================
rororo.annotations
==================

Internal module to keep all reusable type annotations for the project in one
place.

"""

import types
from typing import Any, Dict, TypeVar, Union


DictStrInt = Dict[str, int]
DictStrAny = Dict[str, Any]
Settings = Union[types.ModuleType, DictStrAny]
T = TypeVar('T')
