from dataclasses import dataclass
from typing import Type, Any

from sqlalchemy import RowMapping, select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.db.sql.models.models import Activity
from src.infra.repos.base import BaseRepository


@dataclass(eq=False)
class ActivityRepository(BaseRepository):
    model: Type[Activity] = Activity

    async def read(
        self, data: dict[Any, Any], session: AsyncSession
    ) -> RowMapping | None:
        query = select(
            self.model.id,
            self.model.code,
            self.model.name,
        ).filter_by(**data)
        result = await session.execute(query)
        return result.mappings().fetchone()

    async def create(
        self, data: dict[Any, Any], session: AsyncSession
    ) -> RowMapping | None:
        query = (
            insert(self.model)
            .values(data)
            .returning(
                self.model.id,
                self.model.code,
                self.model.name,
            )
        )
        created_entity = await session.execute(query)
        return created_entity.mappings().fetchone()
