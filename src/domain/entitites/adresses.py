from dataclasses import dataclass, field
from typing import Optional

from src.domain.entitites.base import BaseEntity


@dataclass(eq=False)
class AddressEntity(BaseEntity):
    region: Optional[str]
    municipality: Optional[str]
    locality: Optional[str]
    street: Optional[str]
    postal_code: Optional[str]
    building: Optional[str]
    contractor_id: Optional[int] = field(default=None)

    def to_dict(self):
        return {
            "contractor_id": self.contractor_id,
            "region": self.region,
            "municipality": self.municipality,
            "locality": self.locality,
            "street": self.street,
            "postal_code": self.postal_code,
            "building": self.building,
        }
