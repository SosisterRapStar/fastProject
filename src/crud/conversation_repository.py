import uuid

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.crud.repo_abstract import CRUDAlchemyRepository
from src.models.chat_models import Conversation, UserConversationSecondary, Message
from src.models.user_model import User


class ConversationRepository(CRUDAlchemyRepository):
    _model = Conversation

    # TODO: do something with session identity map for caching
    # TODO: errors handling

    async def get_conv_users(self, conv_id: uuid.UUID) -> list["Conversation"]:
        stmt = (
            select(User)
            .join(UserConversationSecondary, Conversation.id == UserConversationSecondary.conversation_id)
            .join(User, User.id == UserConversationSecondary.user_id)
            .where(User.id == conv_id)
        )
        res = await self.session.scalars(stmt)
        return list(res.all())

    async def get_user_messages(self, user_id: uuid.UUID):
        user = await self.get_user_with_messages(user_id)
        return user.messages

    async def get_user_with_messages(self, user_id: uuid.UUID) -> User:
        stmt = select(User).where(User.id == user_id).options(joinedload(User.conversations))
        user = await self.session.scalar(stmt)
        return user








