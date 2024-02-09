from typing import Type

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase


async def get_smth_id_by_name(
    model: Type[Type[DeclarativeBase]],
    session: AsyncSession,
    smth_name: str,
) -> Type[Type[DeclarativeBase]]:

    stmt = select(model.id).where(model.name == smth_name)
    smth_id = await session.scalar(stmt)
    return smth_id
