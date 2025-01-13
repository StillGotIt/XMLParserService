from dataclasses import dataclass
from typing import Optional

from src.domain.entitites.base import BaseEntity


@dataclass(eq=False)
class ContractorEntity(BaseEntity):
    full_name: str
    short_name: Optional[str]
    kpp: str
    inn: str
    ogrn: str  # noqa

    def to_dict(self):
        return {
            "full_name": self.full_name,
            "short_name": self.short_name,
            "kpp": self.kpp,
            "inn": self.inn,
            "ogrn": self.ogrn,  # noqa
        }


@dataclass(eq=False)
class ContractorWithIdEntity(ContractorEntity):
    id: int

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "short_name": self.short_name,
            "kpp": self.kpp,
            "inn": self.inn,
            "ogrn": self.ogrn,  # noqa
        }
