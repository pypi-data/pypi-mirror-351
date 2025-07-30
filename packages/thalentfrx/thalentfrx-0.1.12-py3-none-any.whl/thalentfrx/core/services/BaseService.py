import logging
from typing import Generic, TypeVar

from pydantic import BaseModel

from thalentfrx.configs.Logger import get_logger
from thalentfrx.core.entities.BaseEntity import BaseEntity
from thalentfrx.core.entities.ListParam import ListParam
from thalentfrx.core.entities.PageRecord import PageRecord
from thalentfrx.core.entities.PagingParam import PagingParam

# Entity = TypeVar('Entity', bound=BaseModel)
# Repository = TypeVar('Repository', bound=BaseRepository)

Entity = TypeVar('Entity')
Repository = TypeVar('Repository')

class BaseService(Generic[Entity, Repository]):
    # Logger
    logger: logging.Logger = get_logger(__name__)
    uvicorn_logger: logging.Logger = logging.getLogger(
        "uvicorn.error"
    )

    def __init__(self, repo: Repository) -> None:
        self.repo = repo

    def get(self, entity_id: str) -> Entity:
        return self.repo.get_entity(entity_id)

    def list(
            self,
            list_param: ListParam
    ) -> PageRecord[Entity]:
        return self.repo.list_of_entity(list_param)

    def paging(
            self,
            paging_param: PagingParam
    ) -> PageRecord[Entity]:
        return self.repo.paging_of_entity(paging_param)

    def delete(self, entity_id: str) -> None:
        self.repo.delete_entity(entity_id)


    def create(self, dto: BaseModel) -> BaseEntity:
        pass

    def update(self, dto: BaseModel) -> BaseEntity:
        pass

    def soft_delete(self, dto: BaseModel) -> BaseEntity:
        pass

    def restore(self, dto: BaseModel) -> BaseEntity:
        pass