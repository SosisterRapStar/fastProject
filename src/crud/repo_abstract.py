from abc import ABC, abstractmethod
from typing import Type

from pydantic import BaseModel
from typing_extensions import Unpack
from sqlalchemy.ext.asyncio import AsyncSession
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


class CRUDAlchemyRepository(CRUDRepository):
    _model: Type[Base] = None

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, data: dict) -> Base:
        # TODO: переработать работу с сессией
        new_obj = self._model(**data)
        self._session.add(new_obj)

        await self._session.commit()  # подразумевается что сессия уже открыта
        return new_obj

    async def get(self, **criteries: Unpack[NameOrId | None]) -> Base:
        res = await get_object(
            async_session=self._session,
            model=self._model,
            **criteries,
        )
        return res

    async def get_all(self) -> list[Base]:
        # В данном случае функция вернет все записи

        res = await get_object(async_session=self._session, model=self._model)

        return res

    async def update(self, data: dict, model_object: Base | None = None, **criteries: Unpack[NameOrId]):

        updated = await update_object(
            async_session=self._session,
            model=self._model,
            data=data,
            model_object=model_object,
            **criteries,
        )

        await self._session.commit()
        return updated

    async def delete(
        self,
        **criteries: Unpack[NameOrId],
    ) -> None:
        returned_id = await delete_obj(
            async_session=self._session,
            model=self._model,
            **criteries,
        )
        await self._session.commit()
        return returned_id

