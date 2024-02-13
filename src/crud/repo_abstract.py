import uuid
from abc import ABC, abstractmethod

from typing import Type, Unpack

from sqlalchemy import insert, Result, select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.errors import RecordNotFoundError
from src.crud.utils import get_object, NameOrId, update_object, delete_obj
from src.models import Base


class CRUDRepository(ABC):

    @abstractmethod
    async def create(self, data: dict):
        raise NotImplementedError

    @abstractmethod
    async def get(self, **criteries):
        raise NotImplementedError

    @abstractmethod
    async def get_all(self):
        raise NotImplementedError

    @abstractmethod
    async def update(self, data: dict, **criteries):
        raise NotImplementedError

    @abstractmethod
    async def delete(self, **criteries):
        raise NotImplementedError


# repo for add some things that are connected with other models
class AddToDeleteFromRepository(ABC):
    model = None

    @abstractmethod
    async def add_to(self):
        raise NotImplementedError

    @abstractmethod
    async def delete_from(self):
        raise NotImplementedError


class CRUDAlchemyRepository(CRUDRepository):
    model: Type[Base] = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: dict) -> uuid.UUID | int:
        stmt = insert(self.model).values(**data).returning(self.model.id)
        res: Result = await self.session.execute(stmt)
        return res.scalar_one()

    async def get(self, **criteries: Unpack[NameOrId | None]) -> Base:
        res = await get_object(
            async_session=self.session,
            model=self.model,
            **criteries,
        )
        return res

    async def get_all(self) -> list[Base]:
        # В данном случае функция вернет все записи
        res = await get_object(async_session=self.session, model=self.model)
        return res

    async def update(self, data: dict, **criteries: Unpack[NameOrId]):
        await update_object(
            async_session=self.session,
            model=self.model,
            data=data,
            **criteries,
        )

    async def delete(
        self,
        **criteries: Unpack[NameOrId],
    ) -> None:
        await delete_obj(
            async_session=self.session,
            model=self.model,
            **criteries,
        )
