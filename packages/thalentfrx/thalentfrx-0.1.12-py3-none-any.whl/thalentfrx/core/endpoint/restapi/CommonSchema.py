from typing import List, Optional

from pydantic import BaseModel, Field


class Filter(BaseModel):
    property: str = Field()
    operator: str= Field()
    value: str= Field()


class Sort(BaseModel):
    property: str = Field()
    dir: str = Field()


class ListParamSchema(BaseModel):
    filter: Optional[List[Filter]] = [],
    sort: Optional[List[Sort]] = [],
    page_size: Optional[int] = 10,
    start_index: Optional[int] = 0,


class PagingParamSchema(BaseModel):
    filter: Optional[List[Filter]] = [],
    sort: Optional[List[Sort]] = [],
    page_size: Optional[int] = 10,
    page: Optional[int] = 1,
