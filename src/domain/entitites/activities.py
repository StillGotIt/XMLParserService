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


@dataclass(eq=False)
class ActivityWithCompanyIdEntity(ActivityEntity):
    contractor_id: int

    def to_dict(self):
        return {
            "contractor_id": self.contractor_id,
            "code": self.code,
            "name": self.name,
        }

    def to_full_dict(self):
        return {
            "contractor_id": self.contractor_id,
            "code": self.code,
            "name": self.name,
        }


@dataclass(eq=False)
class ActivityWithIdCompanyIdEntity(ActivityWithCompanyIdEntity):
    id: int

    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
        }

    def to_full_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
        }


@dataclass(eq=False)
class ContractorActivityEntity(BaseEntity):
    contractor_id: int
    activity_id: int

    def to_dict(self):
        return {
            "contractor_id": self.contractor_id,
            "activity_id": self.activity_id,
        }
