from dataclasses import dataclass
from typing import Optional

from src.domain.entitites.base import BaseEntity


@dataclass(eq=False)
class ActivityEntity(BaseEntity):
    code: Optional[str]
    name: Optional[str]

    def to_dict(self):
        return {
            "code": self.code,
            "name": self.name,
        }

    def to_full_dict(self):
        return {
            "code": self.code,
            "name": self.name,
        }

    def __eq__(self, other):
        return self.name == other.name and self.code == other.code

    def __hash__(self):
        return hash(self.name)


@dataclass(eq=False)
class ActivityModelEntity(BaseEntity):
    id: int
    code: Optional[str]
    name: Optional[str]

    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
        }
