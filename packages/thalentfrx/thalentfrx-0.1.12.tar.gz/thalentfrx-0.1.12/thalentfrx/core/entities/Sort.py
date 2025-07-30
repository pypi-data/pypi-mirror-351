from enum import Enum

from pydantic import BaseModel


class SortDirections(Enum):
    ASC = "asc"
    DESC = "desc"


class Sort(BaseModel):
    property: str
    dir: SortDirections
