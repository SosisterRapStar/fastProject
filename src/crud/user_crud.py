import uuid

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.orm import selectinload

from src.models.user_model import User
from src.schemas.users import User_on_response, User_on_request, User_for_update


async def create_user(async_session: AsyncSession, user: User_on_request) -> User:
    new_user = User(**user.model_dump())
    async_session.add(new_user)
    await async_session.commit()
    return new_user


async def delete_user(
    async_session: AsyncSession,
    user: User_on_request,
):
    pass


async def update_user(
    async_session: AsyncSession,
    user_db: User,
    user_update: User_for_update,
) -> User:
    for name, value in user_update.model_dump(exclude_unset=True).items():
        setattr(user_db, name, value)
    await async_session.commit()
    return user_db


async def get_users(async_session: AsyncSession) -> list[User]:
    stmt = select(User)
    result: Result = await async_session.execute(stmt)
    return list(result.scalars().all())


# async def load_user_with_convs(user_id: uuid.UUID,
#                                async_session: AsyncSession, ) -> User:
#     stmt = select(User).where(User.id == user_id).options(selectinload(User.conversations))
#     # user_with_convs = await get_user_or_404(stmt, session=session)
#     user = await async_session.scalar(stmt)
#     return user
