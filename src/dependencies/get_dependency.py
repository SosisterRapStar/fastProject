import uuid
from typing import Annotated

from fastapi import Path, HTTPException, Depends
from sqlalchemy import select, Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.crud import user_crud
from src.dependencies.session_dependency import session_dep

from src.models.user_model import User


# TODO: перенести в user_crud, а здесь вызывать функции
async def get_user_stmt(criteria):
    return select(User).where(criteria)


async def get_user_or_404(stmt: Select, session: AsyncSession):
    user = await session.scalar(stmt)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def user_by_id(user_id: uuid.UUID,
                     session: session_dep, ) -> User:
    stmt = await get_user_stmt(User.id == user_id)
    return await get_user_or_404(stmt=stmt, session=session)


async def user_by_name(user_name: str,
                       session: session_dep, ) -> User:
    stmt = await get_user_stmt(User.name == user_name)
    return await get_user_or_404(stmt=stmt, session=session)


# async def load_user_convs(user_id: uuid.UUID,
#                           session: session_dep, ) -> User:
#     stmt = select(User).where(User.id == user_id).options(selectinload(User.conversations))
#     # user_with_convs = await get_user_or_404(stmt, session=session)
#     user = await session.scalar(stmt)
#     return user

# load_user_with_convs = Annotated[User, Depends(load_user_convs)]
get_by_id_dep = Annotated[User, Depends(user_by_id)]
get_by_name = Annotated[User, Depends(user_by_name)]
