from dataclasses import dataclass

from src.infra.db.sql.models.base import BaseSQLModel
from src.infra.db.sql.models.models import Activity
from src.infra.repos.base import BaseRepository


@dataclass(eq=False)
class ActivityRepo(BaseRepository):
    model: BaseSQLModel = Activity
