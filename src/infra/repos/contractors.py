from dataclasses import dataclass

from src.infra.db.sql.models.base import BaseSQLModel
from src.infra.db.sql.models.models import Contractor
from src.infra.repos.base import BaseRepository


@dataclass(eq=False)
class ContractorRepo(BaseRepository):
    model: BaseSQLModel = Contractor
