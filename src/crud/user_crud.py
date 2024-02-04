import uuid

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from src.models.user_model import User
from src.schemas.users import User_on_response, User_on_request


async def create_user(async_session: AsyncSession, user: User_on_request) -> User:
    new_user = User(**user.model_dump())
    async_session.add(new_user)
    await async_session.commit()
    return new_user


async def delete_user(
        async_session: async_sessionmaker[AsyncSession],
        user: User_on_request,
):
    pass


async def update_user(
        async_session: async_sessionmaker[AsyncSession],
        user: User_on_request,
):
    pass


async def get_user_by_id(
        async_session: AsyncSession,
        user_id: uuid.UUID,
) -> User | None:
    stmt = select(User).where(User.id == user_id)
    result: Result = await async_session.execute(stmt)
    return result.scalar()


async def get_users(async_session: AsyncSession) -> list[User]:
    stmt = select(User)
    result: Result = await async_session.execute(stmt)
    return list(result.scalars().all())
