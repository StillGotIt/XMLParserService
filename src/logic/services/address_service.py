from dataclasses import dataclass

from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.converters.entity_converters import to_address_entity
from src.domain.entitites.adresses import AddressEntity
from src.domain.entitites.base import BaseEntity
from src.infra.repos.adresses import AddressRepository


@dataclass(eq=False)
class AddressService:
    repository: AddressRepository

    async def get_or_create(
        self, entity: AddressEntity, session: AsyncSession
    ) -> BaseEntity:
        try:
            if address_entity := await self.repository.read(
                data=entity.to_dict(), session=session
            ):
                return to_address_entity(address_entity)
            return to_address_entity(
                await self.repository.create(data=entity.to_dict(), session=session)
            )

        except IntegrityError as e:
            raise ValueError(f"Integrity error: {e.orig}, {entity.to_dict()}")

        except SQLAlchemyError as e:
            raise e.args
