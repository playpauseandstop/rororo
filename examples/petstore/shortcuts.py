from typing import List

from .data import Pet
from .exceptions import ObjectDoesNotExist


def get_pet_or_404(pets: List[Pet], pet_id: int) -> Pet:
    found = [item for item in pets if item.id == pet_id]
    if not found:
        raise ObjectDoesNotExist("Pet")
    return found[0]
