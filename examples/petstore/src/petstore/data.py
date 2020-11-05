from typing import Optional

import attr

from rororo.annotations import DictStrAny


@attr.dataclass(frozen=True, slots=True)
class NewPet:
    name: str
    tag: Optional[str]

    def to_pet(self, pet_id: int) -> "Pet":
        """
        Convert this variant as - variant.

        Args:
            self: (todo): write your description
            pet_id: (str): write your description
        """
        return Pet(id=pet_id, name=self.name, tag=self.tag)


@attr.dataclass(frozen=True, slots=True)
class Pet(NewPet):
    id: int  # noqa: A003, VNE003

    def to_dict(self) -> DictStrAny:
        """
        Convert this tag as a dictionary.

        Args:
            self: (todo): write your description
        """
        if self.tag:
            return {"id": self.id, "name": self.name, "tag": self.tag}
        return {"id": self.id, "name": self.name}
