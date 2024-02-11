import uuid
from typing import Type, Dict, Literal, Any, Coroutine, Optional
from typing_extensions import Unpack, TypedDict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from src.models import Base


class NameId(TypedDict):
    name: str
    id: uuid.UUID


async def get_object(
        async_session: AsyncSession,
        model: Type[Base],
        **criteries: Unpack[NameId | None],
) -> Base | list[Base]:
    if "name" not in criteries.keys() and "id" not in criteries.keys():
        stmt = select(model)
        models = await async_session.scalars(stmt)
        return list(models)

    if 'name' in criteries:
        stmt = select(model).where(model.name == criteries['name'])
        model = await async_session.scalar(stmt)
        return model

    else:
        stmt = select(model).where(model.id == criteries['id'])
        model = await async_session.scalar(stmt)
        return model
