from abc import abstractmethod, ABC
from dataclasses import dataclass


@dataclass(eq=False)
class BaseEntity(ABC):
    @abstractmethod
    def to_dict(self):
        ...
