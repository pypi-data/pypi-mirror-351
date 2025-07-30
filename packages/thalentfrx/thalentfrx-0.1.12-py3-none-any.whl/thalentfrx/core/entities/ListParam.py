from typing import List

from pydantic import BaseModel

from thalentfrx.core.entities.Sort import Sort
from thalentfrx.core.entities.Filter import Filter


class ListParam(BaseModel):
    filter: List[Filter] = [],
    sort: List[Sort] = [],
    limit: int = 10,
    start: int = 0,
