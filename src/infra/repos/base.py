from dataclasses import dataclass
from typing import Any, Sequence


from sqlalchemy import RowMapping, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.db.sql.models.base import BaseSQLModel


@dataclass(eq=False)
class BaseRepository:
    model: BaseSQLModel

    async def create(self, data: dict[Any, Any], session: AsyncSession) -> Sequence[RowMapping]:
        query = (
            insert(self.model)
            .values(**data)
            .returning(
                self.model,
            )
        )
        result = await session.execute(query)
        return result.mappings().fetchone()

    async def read(self, data: dict[Any, Any], session: AsyncSession) -> Sequence[RowMapping]:
        query = select(
            self.model,
        ).filter_by(**data)
        result = await session.execute(query)
        return result.mappings().fetchone()
