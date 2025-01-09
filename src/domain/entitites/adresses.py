from dataclasses import dataclass

from src.domain.entitites.base import BaseEntity


@dataclass(eq=False)
class AddressEntity(BaseEntity):
    region: str
    city: str
    street: str
    postal_code: str
    house: str

    def to_dict(self):
        return {
            "region": self.region,
            "city": self.city,
            "street": self.street,
            "postal_code": self.postal_code,
            "house": self.house,
        }


@dataclass(eq=False)
class AddressEntityWithId(AddressEntity):
    id: int

    def to_dict(self):
        return {
            "id": self.id,
            "region": self.region,
            "city": self.city,
            "street": self.street,
            "postal_code": self.postal_code,
            "house": self.house,
        }
