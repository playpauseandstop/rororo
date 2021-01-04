from typing import Any, Dict, List, Union

from ..annotations import TypedDict


SecurityDict = Dict[str, List[str]]


class ValidateEmailKwargsDict(TypedDict, total=False):
    allow_smtputf8: bool
    allow_empty_local: bool
    check_deliverability: bool
    timeout: Union[int, float]
    dns_resolver: Any
