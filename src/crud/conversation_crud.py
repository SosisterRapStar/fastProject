import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.orm import selectinload

from src.models.base import db_handler
from src.models.chat_models import Conversation, UserConversationSecondary
from src.models.user_model import User
from src.schemas.conversation import ConversationRequest


# TODO: исправить пиздец этот
async def get_empty_conv(
        conversation_schema: ConversationRequest,
        creator_id: uuid.UUID,
) -> Conversation:
    new_conv = Conversation(
        **conversation_schema.model_dump(),
        user_admin_fk=creator_id,
    )
    return new_conv


async def create_conversation_and_add_user(
        async_session: AsyncSession,
        user_id: uuid.UUID,
        conversation_schema: ConversationRequest,
):
    new_conv = await get_empty_conv(conversation_schema, user_id)
    async_session.add(new_conv)
    await async_session.commit()
    await async_session.refresh(new_conv)
    await add_user_to_conv(async_session, user_id, new_conv.id)
    await async_session.commit()


async def add_user_to_conv(
        async_session: AsyncSession,
        user_id: uuid.UUID,
        conv_id: uuid.UUID,
):
    sec = UserConversationSecondary()
    sec.user_id = user_id
    sec.conversation_id = conv_id
    async_session.add(sec)
    await async_session.commit()


async def demo_add_user_to_conversation(
        async_session: AsyncSession,
        user_name: str,
        conv_name: str,
        conversation_schema: ConversationRequest | None = None,
):
    stmt = (
        select(User)
        .where(User.name == user_name)
        .options(selectinload(User.conversations))
    )
    user = await async_session.scalar(stmt)
    conv = await get_conv_by_name(async_session, conv_name)
    user.conversations.append(conv)
    await async_session.commit()


async def get_user_convs(async_session: AsyncSession, user_name: str) -> list[Conversation]:
    stmt = (
        select(User)
        .where(User.name == user_name)
        .options(selectinload(User.conversations))
    )
    user = await async_session.scalar(stmt)
    return user.conversations


async def get_users_in_conv(async_session: AsyncSession, conv_name: str, ) -> list[User]:
    stmt = select(Conversation).where(Conversation.name == conv_name).options(selectinload(Conversation.users))
    conv = await async_session.scalar(stmt)
    return conv.users


async def get_conv_by_name(
        async_session: AsyncSession,
        conv_name: str,
):
    stmt = select(Conversation).where(Conversation.name == conv_name)
    return await async_session.scalar(stmt)


async def delete_conversation(async_session: async_sessionmaker):
    pass


async def update_conversation(async_session: async_sessionmaker):
    pass
