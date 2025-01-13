from dataclasses import dataclass

from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.converters.entity_converters import to_contractor_entity
from src.domain.entitites.base import BaseEntity
from src.domain.entitites.contractors import ContractorWithIdEntity

from src.infra.repos.contractors import ContractorRepository


@dataclass(eq=False)
class ContractorService:
    repository: ContractorRepository

    async def get_or_create(
        self, entity: BaseEntity, session: AsyncSession
    ) -> ContractorWithIdEntity:
        try:
            if contractor_entity := await self.repository.read(
                data=entity.to_dict(), session=session
            ):
                return to_contractor_entity(contractor_entity)
            return to_contractor_entity(
                await self.repository.create(data=entity.to_dict(), session=session)
            )

        except IntegrityError as e:
            raise ValueError(f"Integrity error: {e.orig}, {entity.to_dict()}")

        except SQLAlchemyError as e:
            raise e.args
