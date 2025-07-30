import logging
from typing import Generic, TypeVar

from pydantic import BaseModel

from thalentfrx.configs.Logger import get_logger
from thalentfrx.core.entities.BaseEntity import BaseEntity
from thalentfrx.core.entities.ListParam import ListParam
from thalentfrx.core.entities.PageRecord import PageRecord
from thalentfrx.core.entities.PagingParam import PagingParam
from thalentfrx.core.repositories.AsyncBaseRepository import AsyncBaseRepository

# Entity = TypeVar('Entity', bound=BaseModel)
# Repository = TypeVar('Repository', bound=BaseRepository)

Entity = TypeVar('Entity')
Repository = TypeVar('Repository')


class AsyncBaseService(Generic[Entity, Repository]):
    # Logger
    logger: logging.Logger = get_logger(__name__)
    uvicorn_logger: logging.Logger = logging.getLogger(
        "uvicorn.error"
    )

    def __init__(self, repo: AsyncBaseRepository) -> None:
        self.repo = repo

    async def get(self, entity_id: str) -> Entity:
        return await self.repo.get(entity_id)

    async def list(
            self,
            list_param: ListParam
    ) -> PageRecord[Entity]:
        return await self.repo.list(list_param)

    async def paging(
            self,
            paging_param: PagingParam
    ) -> PageRecord[Entity]:
        return await self.repo.paging(paging_param)

    async def delete(self, entity_id: str) -> None:
        await self.repo.delete(entity_id)


    async def create(self, dto: BaseModel) -> BaseEntity:
        pass

    async def update(self, dto: BaseModel) -> BaseEntity:
        pass

    async def soft_delete(self, dto: BaseModel) -> BaseEntity:
        pass

    async def restore(self, dto: BaseModel) -> BaseEntity:
        pass