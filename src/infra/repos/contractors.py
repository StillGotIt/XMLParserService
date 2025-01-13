from dataclasses import dataclass
from typing import Type, Any

from sqlalchemy import RowMapping, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.db.sql.models.models import Contractor
from src.infra.repos.base import BaseRepository


@dataclass(eq=False)
class ContractorRepository(BaseRepository):
    model: Type[Contractor] = Contractor

    async def read(
        self, data: dict[Any, Any], session: AsyncSession
    ) -> RowMapping | None:
        query = select(
            self.model.id,
            self.model.full_name,
            self.model.short_name,
            self.model.kpp,
            self.model.inn,
            self.model.ogrn,
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
                self.model.full_name,
                self.model.short_name,
                self.model.kpp,
                self.model.inn,
                self.model.ogrn,
            )
        )
        created_entity = await session.execute(query)
        return created_entity.mappings().fetchone()
