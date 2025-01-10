from dataclasses import dataclass

from src.infra.db.sql.models.base import BaseSQLModel
from src.infra.db.sql.models.models import Address
from src.infra.repos.base import BaseRepository


@dataclass(eq=False)
class AddressRepo(BaseRepository):
    model: BaseSQLModel = Address
