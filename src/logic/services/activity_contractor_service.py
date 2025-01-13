from dataclasses import dataclass

from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.converters.entity_converters import to_activity_contractor_entity
from src.domain.entitites.activities import ContractorActivityEntity
from src.domain.entitites.base import BaseEntity
from src.infra.repos.activities_contractors import ActivityContractorRepository


@dataclass(eq=False)
class ActivityContractorService:
    repository: ActivityContractorRepository

    async def get_or_create(
        self, entity: BaseEntity, session: AsyncSession
    ) -> BaseEntity:
        try:
            if activity_entity := await self.repository.read(
                data=entity.to_dict(), session=session
            ):
                return to_activity_contractor_entity(activity_entity)
            return to_activity_contractor_entity(
                await self.repository.create(data=entity.to_dict(), session=session)
            )

        except IntegrityError as e:
            raise ValueError(f"Integrity error: {e.orig}, {entity.to_dict()}")

        except SQLAlchemyError as e:
            raise e.args

    async def bulk_create(
        self, entities: list[ContractorActivityEntity], session: AsyncSession
    ) -> BaseEntity:
        try:
            return to_activity_contractor_entity(
                await self.repository.create(
                    data=[entity.to_dict() for entity in entities], session=session
                )
            )

        except IntegrityError as e:
            raise ValueError(f"Integrity error: {e.orig}")

        except SQLAlchemyError as e:
            raise e.args
