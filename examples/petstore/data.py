from typing import Optional

import attr


@attr.dataclass(frozen=True, slots=True)
class NewPet:
    name: str
    tag: Optional[str]

    def to_pet(self, pet_id: int) -> "Pet":
        return Pet(id=pet_id, name=self.name, tag=self.tag)


@attr.dataclass(frozen=True, slots=True)
class Pet(NewPet):
    id: int
