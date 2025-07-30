from typing import Any, Generic, List, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class PageRecord(BaseModel, Generic[T]):
    count: int
    rows: List[T]
