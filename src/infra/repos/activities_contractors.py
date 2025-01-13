from dataclasses import dataclass
from typing import Type, Any

from sqlalchemy import select, RowMapping, insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.db.sql.models.models import ActivityContractor
from src.infra.repos.base import BaseRepository


@dataclass(eq=False)
class ActivityContractorRepository(BaseRepository):
    model: Type[ActivityContractor] = ActivityContractor

    async def read(
        self, data: dict[Any, Any], session: AsyncSession
    ) -> RowMapping | None:
        query = select(self.model.contractor_id, self.model.activity_id).filter_by(
            **data
        )
        result = await session.execute(query)
        return result.mappings().fetchone()

    async def create(
        self, data: dict[Any, Any] | list[dict[Any, Any]], session: AsyncSession
    ) -> RowMapping | None:
        query = (
            insert(self.model)
            .values(data)
            .returning(self.model.contractor_id, self.model.activity_id)
        )
        created_entity = await session.execute(query)
        return created_entity.mappings().fetchone()
