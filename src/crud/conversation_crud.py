import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.orm import selectinload

from src.models.base import db_handler
from src.models.chat_models import Conversation, UserConversationSecondary
from src.models.user_model import User
from src.schemas.conversation import ConversationRequest


async def get_empty_conv(conversation_schema: ConversationRequest, creator_id: uuid.UUID, ) -> Conversation:
    new_conv = Conversation(**conversation_schema.model_dump(),
                            user_admin_fk=creator_id,
                            )
    return new_conv


async def create_conversation_and_add_user(
        async_session: AsyncSession,
        user_id: uuid.UUID,
        conversation_schema: ConversationRequest,
):
    new_conv = await get_empty_conv(conversation_schema, user_id)
    await add_user_to_conv(async_session, user_id, new_conv.id)
    await async_session.commit()


async def add_user_to_conv(
        async_session: AsyncSession,
        user_id: uuid.UUID,
        conv_id: uuid.UUID,
):
    sec = await create_secondary()
    sec.user_id = user_id
    sec.conversation_id = conv_id
    async_session.add(sec)


async def demo_create_conversation(
        async_session: AsyncSession,
        user_name: str,
        conversation_schema: ConversationRequest,
):
    stmt = select(User).where(User.name == user_name).options(selectinload(User.conversations))
    user = async_session.scalar(stmt)

async def get_conv_by_name(async_session: session)



async def create_secondary(session: AsyncSession):
    return UserConversationSecondary()


async def delete_conversation(async_session: async_sessionmaker):
    pass


async def update_conversation(async_session: async_sessionmaker):
    pass
