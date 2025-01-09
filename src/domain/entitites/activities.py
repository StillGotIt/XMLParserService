from dataclasses import dataclass
from datetime import datetime

from src.domain.entitites.base import BaseEntity


@dataclass(eq=False)
class ActivityWithoutCompanyIdEntity(BaseEntity):
    code: str
    name: str
    record_date: datetime
    is_main_activity: bool

    def to_dict(self):
        return {
            "code": self.code,
            "name": self.name,
            "record_date": self.record_date,
            "is_main_activity": self.is_main_activity,
        }


@dataclass(eq=False)
class ActivityWithCompanyIdEntity(ActivityWithoutCompanyIdEntity):
    id: int

    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "record_date": self.record_date,
            "is_main_activity": self.is_main_activity,
        }
