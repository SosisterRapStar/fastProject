import uuid
from typing import Type, Tuple
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

    stmt = await get_statement(model=model, criterias=criteries)
    obj = await async_session.scalar(stmt)

    if obj is None:
        raise RecordNotFoundError

    return obj


async def get_statement(model: Type[Base], criterias: dict[str, str]):
    first_key = next(iter(criterias))
    value = criterias[first_key]  # HOROSHAYA RABOTA
    stmt = (
        select(model).
        where(getattr(model, first_key) == value)
    )
    return stmt


async def update_object(
        async_session: AsyncSession,
        model: Type[Base],
        data: dict,
        model_object: Base | None = None,
        **criteries: Unpack[NameOrId],
) -> Base:
    if model_object:
        return await update_using_object(model_object, data)

    if "name" not in criteries.keys() and "id" not in criteries.keys():
        raise ValueError("You must specify id or name")

    stmt = await get_update_statement(data=data, model=model, criterias=criteries)

    result: Result = await async_session.execute(stmt)
    return result.scalar_one()


async def get_update_statement(model: Type[Base], data: dict, criterias: dict[str, str]):
    first_key = next(iter(criterias))
    value = criterias[first_key]  # HOROSHAYA RABOTA
    stmt = (
        update(model)
        .where(getattr(model, first_key) == value)
        .values(**data)
        .returning(model)
    )
    return stmt


async def update_using_object(model_object: Base, data: dict):
    for key, arg in data.items():
        setattr(model_object, key, arg)
    return model_object


async def delete_obj(
        async_session: AsyncSession,
        model: Type[Base],
        **criterias: Unpack[NameOrId],
) -> None:
    if "name" not in criterias.keys() and "id" not in criterias.keys():
        raise ValueError("You must specify id or name")

    stmt = await get_delete_statement(model=model, criterias=criterias)
    result: Result = await async_session.execute(stmt)
    return result.scalar_one()


async def get_delete_statement(model: Type[Base], criterias: dict[str, str]):
    first_key = next(iter(criterias))
    value = criterias[first_key]  # HOROSHAYA RABOTA
    stmt = (
        delete(model).
        where(getattr(model, first_key) == value).
        returning(model.id)
    )
    return stmt
