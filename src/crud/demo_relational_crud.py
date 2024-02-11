import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.chat_models import UserConversationSecondary, Conversation
from src.models.user_model import User


async def get_user_stmt(criteria):
    return select(Conversation).where(criteria)


async def get_user_convs(async_session: AsyncSession, user_name: str):
    stmt = await get_user_stmt(User.name == user_name)
    stmt = stmt.options(
        selectinload(User.asoc_conversations).joinedload(UserConversationSecondary.user)
    )
    user = await async_session.scalar(stmt)

    return user.conversations


# async def get_user_convs(user_id: uuid.UUID,
#                                async_session: AsyncSession, ) -> User:
#     stmt = select(User).where(User.id == user_id).options(selectinload(User.conversations))
#     # user_with_convs = await get_user_or_404(stmt, session=session)
#     user = await async_session.scalar(stmt)
#     return user
