from typing import List

from pydantic import BaseModel

from thalentfrx.core.entities.Sort import Sort
from thalentfrx.core.entities.Filter import Filter


class PagingParam(BaseModel):
    filter: List[Filter] = [],
    sort: List[Sort] = [],
    page_size: int = 10,
    page: int = 1,
