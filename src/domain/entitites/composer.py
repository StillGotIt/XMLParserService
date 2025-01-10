from dataclasses import dataclass, field

from src.domain.entitites.activities import ActivityWithoutCompanyIdEntity
from src.domain.entitites.adresses import AddressEntity
from src.domain.entitites.contractors import ContractorEntity


@dataclass(eq=False)
class ActivityAddressContractorComposer:
    contractor: ContractorEntity
    address: AddressEntity
    activity: list[ActivityWithoutCompanyIdEntity] = field(default_factory=list)
