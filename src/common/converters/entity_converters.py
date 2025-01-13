from typing import Sequence

from sqlalchemy import RowMapping

from src.domain.entitites.adresses import AddressWithIdEntity
from src.domain.entitites.contractors import ContractorWithIdEntity
from src.domain.entitites.activities import ActivityModelEntity, ContractorActivityEntity


def to_contractor_entity(data: RowMapping):
    return ContractorWithIdEntity(**data)


def to_activity_entity(data: RowMapping):
    return ActivityModelEntity(**data)


def to_activity_contractor_entity(data: RowMapping):
    return ContractorActivityEntity(**data)


def to_address_entity(data: RowMapping):
    return AddressWithIdEntity(**data)
