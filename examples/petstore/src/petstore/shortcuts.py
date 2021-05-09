from typing import List

from rororo.openapi.exceptions import ObjectDoesNotExist

from .data import Pet


def get_pet_or_404(pets: List[Pet], pet_id: int) -> Pet:
    found = [item for item in pets if item.id == pet_id]
    if not found:
        raise ObjectDoesNotExist(message="Requested Pet not found")
    return found[0]
