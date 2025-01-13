from dataclasses import dataclass, field

from src.domain.entitites.activities import ActivityEntity
from src.domain.entitites.adresses import AddressEntity
from src.domain.entitites.base import BaseEntity
from src.domain.entitites.contractors import ContractorEntity, ContractorWithIdEntity


@dataclass(eq=False)
class ActivityAddressContractorComposer(BaseEntity):
    contractor: ContractorEntity
    address: AddressEntity | None
    activity: list[ActivityEntity] | None = field(default_factory=list)

    def to_dict(self):
        return {
            "contractor": self.contractor,
            "address": self.address,
            "activity": self.activity,
        }


@dataclass(eq=False)
class ActivityAddressContractorWithIdComposer(BaseEntity):
    contractor: ContractorWithIdEntity
    address: AddressEntity | None
    activity: list[ActivityEntity] | None = field(default_factory=list)

    def to_dict(self):
        return {
            "contractor": self.contractor,
            "address": self.address,
            "activity": self.activity,
        }
