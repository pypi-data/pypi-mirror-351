import logging
from typing import Generic, Optional, TypeVar, List

from sqlalchemy.ext.asyncio import AsyncSession

from thalentfrx.configs.Logger import get_logger
from thalentfrx.core.entities.BaseEntity import BaseEntity
from thalentfrx.core.entities.Filter import Filter
from thalentfrx.core.entities.ListParam import ListParam
from thalentfrx.core.entities.PageRecord import PageRecord
from thalentfrx.core.entities.PagingParam import PagingParam
from thalentfrx.core.entities.Sort import Sort
from thalentfrx.core.models.BaseModel import EntityMeta
from thalentfrx.core.models.Helpers import Helpers
from thalentfrx.core.repositories.Helpers import filter_query, order_query

# Type definition for Model Type
Model = TypeVar("Model", bound=EntityMeta)


class AsyncBaseRepository(Generic[Model]):
    # Logger
    logger: logging.Logger = get_logger(__name__)
    uvicorn_logger: logging.Logger = logging.getLogger(
        "uvicorn.error"
    )

    def __init__(self, model: Model, session: AsyncSession) -> None:
        self.model = model
        self.session = session

    async def __query(
            self,
            list_filter: Optional[List[Filter]],
            sort: Optional[List[Sort]],
    ):
        q = await self.session.query(self.model)
        if list_filter:
            q = filter_query(q, list_filter, Model.__name__)
        if sort:
            q = order_query(q, sort, Model.__name__)

        return q

    async def _list(
            self,
            list_param: Optional[ListParam] = ListParam(
                filter=[], sort=[], limit=1, start=10
            ),
    ) -> PageRecord:

        data: PageRecord = PageRecord(
            count=0,
            rows=[]
        )
        q = await self.__query(list_param.list_filter, list_param.sort)
        data.count = q.count()
        q = await q.limit(list_param.limit).offset(list_param.start).all()
        data.rows = [row for row in q]
        return data

    async def _paging(
            self,
            paging_param: Optional[PagingParam] = PagingParam(
                filter=[], sort=[], page=1, page_size=10
            ),
    ) -> PageRecord:

        data: PageRecord = PageRecord(
            count=0,
            rows=[]
        )

        q = await self.__query(paging_param.list_filter, paging_param.sort)
        data.count = q.count()
        q = await q.limit(paging_param.page_size).offset(((paging_param.page - 1) * paging_param.page_size)).all()
        data.rows = [row for row in q]
        return data

    async def _get(self, entity_id: str) -> Model:
        data = await self.session.get(self.model, entity_id)
        return data

    async def _create(self, instance: Model, is_transaction: bool = False) -> None:
        instance.row_timespan = Helpers().get_timestamp()
        await self.session.add(instance)
        if not is_transaction:
            await self.session.commit()
            await self.session.refresh(instance)

    async def _update(self, instance: Model, is_transaction: bool = False) -> None:
        instance.row_timespan = Helpers().get_timestamp()
        await self.session.merge(instance)
        if not is_transaction:
            await self.session.commit()

    async def _delete(self, entity_id: str, is_transaction: bool = False) -> None:
        row = await self.session.get(self.model, entity_id)
        await self.session.delete(row)
        if not is_transaction:
            await self.session.commit()
            await self.session.flush()

    async def list_of_entity(
            self,
            param: Optional[ListParam],
    ) -> PageRecord[BaseEntity]:
        pass

    async def paging_of_entity(
            self,
            param: Optional[PagingParam],
    ) -> PageRecord[BaseEntity]:
        pass

    async def get_entity(self, entity_id: str) -> BaseEntity:
        pass

    async def create_entity(
        self,
        entity: BaseEntity,
        is_transaction: bool = False,
    ) -> None:
        pass

    async def modify_entity(
        self,
        entity: BaseEntity,
        is_transaction: bool = False,
    ) -> None:
        pass

    async def delete_entity(
        self,
        entity_id: str,
        is_transaction: bool = False,
    ) -> None:
        pass