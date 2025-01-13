from dataclasses import dataclass

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.converters.entity_converters import to_activity_entity
from src.domain.entitites.activities import ActivityEntity
from src.domain.entitites.base import BaseEntity
from src.infra.repos.activities import ActivityRepository


@dataclass(eq=False)
class ActivityService:
    repository: ActivityRepository

    async def get_or_create(self, entity: ActivityEntity, session:AsyncSession) -> BaseEntity:
        try:
            if activity_entity := await self.repository.read(data=entity.to_dict(), session=session):
                return to_activity_entity(activity_entity)
            return to_activity_entity(await self.repository.create(data=entity.to_dict(), session=session))
        except SQLAlchemyError as e:
            raise e