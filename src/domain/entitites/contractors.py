from dataclasses import dataclass

from src.domain.entitites.base import BaseEntity


@dataclass(eq=False)
class ContractorEntity(BaseEntity):
    full_name: str
    short_name: str
    KPP: str
    INN: str
    OGRN: str  # noqa

    def to_dict(self):
        return {
            "full_name": self.full_name,
            "short_name": self.short_name,
            "KPP": self.KPP,
            "INN": self.INN,
            "OGRN": self.OGRN  # noqa
        }


@dataclass(eq=False)
class ContractorWithId(ContractorEntity):
    id: int

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "short_name": self.short_name,
            "KPP": self.KPP,
            "INN": self.INN,
            "OGRN": self.OGRN}
