import logging
from typing import Generic, Optional, TypeVar, List

from sqlalchemy.orm import Session

from thalentfrx.configs.Logger import get_logger

from thalentfrx.core.entities.ListParam import ListParam
from thalentfrx.core.entities.PageRecord import PageRecord
from thalentfrx.core.entities.PagingParam import PagingParam

from thalentfrx.core.entities.BaseEntity import BaseEntity

from thalentfrx.core.entities.Filter import Filter
from thalentfrx.core.entities.Sort import Sort
from thalentfrx.core.models.Helpers import Helpers
from thalentfrx.core.repositories.Helpers import filter_query, order_query

# Type definition for Model Type
# Model = TypeVar('Model', bound=EntityMeta)
Model = TypeVar('Model')

class BaseRepository(Generic[Model]):
    # Logger
    logger: logging.Logger = get_logger(__name__)
    uvicorn_logger: logging.Logger = logging.getLogger(
        "uvicorn.error"
    )

    def __init__(self, model: Model, session: Session) -> None:
        self.model = model
        self.session = session

    def __get_model_name(self) -> str:
        model_name = self.model.__tablename__.split("_")[1].replace("_", " ").title().replace(" ", "")
        return model_name

    def __query(
            self,
            list_filter: Optional[List[Filter]],
            sort: Optional[List[Sort]],
    ):
        q = self.session.query(self.model)

        context = {
            self.__get_model_name(): self.model,
            **self.model.__dict__,
            **Sort.__dict__,
            **Filter.__dict__,
        }

        if list_filter:
            q = filter_query(q, list_filter, self.__get_model_name(), context)
        if sort:
            q = order_query(q, sort, self.__get_model_name(), context)

        return q

    def _list(
            self,
            list_param: Optional[ListParam] = ListParam(
                filter=[], sort=[], limit=10, start=0
            ),
    ) -> PageRecord:

        data: PageRecord = PageRecord(
            count=0,
            rows=[]
        )
        q = self.__query(list_param.filter, list_param.sort)
        data.count = q.count()
        q = q.limit(list_param.limit).offset(list_param.start).all()
        data.rows = [row for row in q]
        return data

    def _paging(
            self,
            paging_param: Optional[PagingParam] = PagingParam(
                filter=[], sort=[], page=1, page_size=10
            ),
    ) -> PageRecord:

        data: PageRecord = PageRecord(
            count=0,
            rows=[]
        )

        if paging_param.page <= 0:
            paging_param.page = 1

        q = self.__query(paging_param.filter, paging_param.sort)
        data.count = q.count()
        q = q.limit(paging_param.page_size).offset(((paging_param.page - 1) * paging_param.page_size)).all()
        data.rows = [row for row in q]
        return data

    def _get(self, entity_id: str) -> Model:
        data = self.session.get(self.model, entity_id)
        return data

    def _create(self, instance: Model, is_transaction: bool = False) -> None:
        instance.row_timespan = Helpers().get_timestamp()
        self.session.add(instance)
        if not is_transaction:
            self.session.commit()
            self.session.refresh(instance)

    def _update(self, entity_id: str, instance: Model, is_transaction: bool = False) -> None:
        instance.row_timespan = Helpers().get_timestamp()
        self.session.get(self.model, entity_id)
        self.session.merge(instance)
        if not is_transaction:
            self.session.commit()

    def _delete(self, entity_id: str, is_transaction: bool = False) -> None:
        row = self.session.get(self.model, entity_id)
        self.session.delete(row)
        if not is_transaction:
            self.session.commit()
            self.session.flush()

    def list_of_entity(
            self,
            param: Optional[ListParam],
    ) -> PageRecord[BaseEntity]:
        pass

    def paging_of_entity(
            self,
            param: Optional[PagingParam],
    ) -> PageRecord[BaseEntity]:
        pass

    def get_entity(self, entity_id: str) -> BaseEntity:
        pass

    def create_entity(
        self,
        entity: BaseEntity,
        is_transaction: bool = False,
    ) -> None:
        pass

    def modify_entity(
        self,
        entity: BaseEntity,
        is_transaction: bool = False,
    ) -> None:
        pass

    def delete_entity(
        self,
        entity_id: str,
        is_transaction: bool = False,
    ) -> None:
        pass