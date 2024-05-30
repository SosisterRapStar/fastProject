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

    if criteries.get("name", None) is None and criteries.get("id", None) is None:
        stmt = select(model)
        models = await async_session.scalars(stmt)
        return list(models)

    stmt = await get_statement(model=model, criterias=criteries)
    obj = await async_session.scalar(stmt)

    if obj is None:
        raise RecordNotFoundError

    return obj


async def update_object(
    async_session: AsyncSession,
    model: Type[Base],
    data: dict,
    model_object: Base | None = None,
    **criteries: Unpack[NameOrId],
) -> Base:
    if model_object:
        return await update_using_object(async_session, model_object, data)

    if "name" not in criteries.keys() and "id" not in criteries.keys():
        raise ValueError("You must specify id or name")

    stmt = await get_update_statement(data=data, model=model, criterias=criteries)

    result: Result = await async_session.execute(stmt)
    return result.scalar_one()


async def update_using_object(
    async_session: AsyncSession, model_object: Base, data: dict
):
    for key, arg in data.items():
        setattr(model_object, key, arg)
    return model_object


async def delete_obj(
    async_session: AsyncSession,
    model: Type[Base],
    model_obj: Base | None = None,
    **criterias: Unpack[NameOrId],
) -> None:
    if model_obj:
        await async_session.delete(model_obj)
        return model_obj.id
    if "name" not in criterias.keys() and "id" not in criterias.keys():
        raise ValueError("You must specify id or name")

    stmt = await get_delete_statement(model=model, criterias=criterias)
    result: Result = await async_session.execute(stmt)
    return result.scalar()


async def get_statement(model: Type[Base], criterias: dict[str, str]):
    for key in criterias:
        if value := criterias[key]:
            attribute = valid_attribute(model=model, key=key)
            stmt = select(model).where(attribute == value)
            return stmt


async def get_update_statement(
    model: Type[Base], data: dict, criterias: dict[str, str]
):
    for key in criterias:
        if value := criterias[key]:
            attribute = valid_attribute(model=model, key=key)
            stmt = (
                update(model).where(attribute == value).values(**data).returning(model)
            )
            return stmt


async def get_delete_statement(model: Type[Base], criterias: dict[str, str]):
    for key in criterias:
        if value := criterias[key]:
            attribute = valid_attribute(model=model, key=key)
            stmt = delete(model).where(attribute == value).returning(model.id)
            return stmt


def valid_attribute(model, key):
    try:
        attribute = getattr(model, key)
        return attribute
    except AttributeError:
        raise AttributeError(f"There is no such key {key=} in {model=}")
