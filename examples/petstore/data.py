from dataclasses import dataclass
from typing import Optional


@dataclass
class NewPet:
    name: str
    tag: Optional[str]

    def to_pet(self, pet_id: int) -> "Pet":
        return Pet(id=pet_id, name=self.name, tag=self.tag)


@dataclass
class Pet(NewPet):
    id: int
