from dataclasses import dataclass
from typing import Type, Any

from sqlalchemy import select, RowMapping, insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.db.sql.models.models import Address
from src.infra.repos.base import BaseRepository


@dataclass(eq=False)
class AddressRepository(BaseRepository):
    model: Type[Address] = Address

    async def read(
        self, data: dict[Any, Any], session: AsyncSession
    ) -> RowMapping | None:
        query = select(
            self.model.id,
            self.model.contractor_id,
            self.model.region,
            self.model.municipality,
            self.model.locality,
            self.model.street,
            self.model.postal_code,
            self.model.building,
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
                self.model.contractor_id,
                self.model.region,
                self.model.municipality,
                self.model.locality,
                self.model.street,
                self.model.postal_code,
                self.model.building,
            )
        )
        created_entity = await session.execute(query)
        return created_entity.mappings().fetchone()
