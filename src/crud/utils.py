import uuid
from typing import Type
from typing_extensions import Unpack, TypedDict
from sqlalchemy import select, update, delete, Result
from sqlalchemy.ext.asyncio import AsyncSession
from src.crud.exceptions import RecordNotFoundError
from src.models import Base


class NameOrId(TypedDict):
    name: str
    id: uuid.UUID


async def get_object(
    async_session: AsyncSession,
    model: Type[Base],
    **criteries: Unpack[NameOrId | None],
) -> Base | list[Base]:
    if "name" not in criteries.keys() and "id" not in criteries.keys():
        stmt = select(model)
        models = await async_session.scalars(stmt)
        return list(models)

    if "name" in criteries:
        stmt = select(model).where(model.name == criteries["name"])
        obj = await async_session.scalar(stmt)
    else:
        stmt = select(model).where(model.id == criteries["id"])
        obj = await async_session.scalar(stmt)

    if obj is None:
        raise RecordNotFoundError

    return obj


async def update_object(
    async_session: AsyncSession,
    model: Type[Base],
    data: dict,
    **criteries: Unpack[NameOrId],
) -> Base:
    if "name" not in criteries.keys() and "id" not in criteries.keys():
        raise ValueError("You must specify id or name")

    if "name" in criteries:
        stmt = (
            update(model)
            .where(model.name == criteries["name"])
            .values(**data)
            .returning(model)
        )
        result: Result = await async_session.execute(stmt)
        return result.scalar_one()

    else:
        stmt = (
            update(model)
            .where(model.id == criteries["id"])
            .values(**data)
            .returning(model)
        )
        result: Result = await async_session.execute(stmt)
        return result.scalar_one()


async def delete_obj(
    async_session: AsyncSession,
    model: Type[Base],
    **criteries: Unpack[NameOrId],
) -> None:
    if "name" not in criteries.keys() and "id" not in criteries.keys():
        raise ValueError("You must specify id or name")

    if "name" in criteries:
        stmt = delete(model).where(model.name == criteries["name"]).returning(model.id)
        result: Result = await async_session.execute(stmt)
        return result.scalar_one()

    else:
        stmt = delete(model).where(model.id == criteries["id"]).returning(model.id)
        result: Result = await async_session.execute(stmt)
        return result.scalar_one()
