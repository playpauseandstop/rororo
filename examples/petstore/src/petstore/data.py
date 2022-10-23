from typing import Union

import attr

from rororo.annotations import DictStrAny


@attr.dataclass(frozen=True, slots=True)
class NewPet:
    name: str
    tag: Union[str, None]

    def to_pet(self, pet_id: int) -> "Pet":
        return Pet(id=pet_id, name=self.name, tag=self.tag)


@attr.dataclass(frozen=True, slots=True)
class Pet(NewPet):
    id: int  # noqa: A003, VNE003

    def to_dict(self) -> DictStrAny:
        if self.tag:
            return {"id": self.id, "name": self.name, "tag": self.tag}
        return {"id": self.id, "name": self.name}
