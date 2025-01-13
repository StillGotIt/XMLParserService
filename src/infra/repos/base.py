from abc import abstractmethod, ABC
from dataclasses import dataclass
from typing import Any, Type

from sqlalchemy import RowMapping, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.db.sql.models.base import BaseSQLModel


@dataclass(eq=False)
class BaseRepository(ABC):
    model: Type[BaseSQLModel]

    @abstractmethod
    async def create(self, data: dict[Any, Any], session: AsyncSession) -> RowMapping:
        ...

    @abstractmethod
    async def read(self, data: dict[Any, Any], session: AsyncSession) -> RowMapping | None:
        ...
