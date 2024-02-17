import uuid

from sqlalchemy import select, insert
from sqlalchemy.orm import joinedload

from src.crud.repo_abstract import CRUDAlchemyRepository
from src.models.chat_models import Conversation, UserConversationSecondary, Message
from src.models.user_model import User


class ConversationRepository(CRUDAlchemyRepository):
    _model = Conversation

    # TODO: do something with session identity map for caching
    # TODO: errors handling

    async def get_users(self, conv_id: uuid.UUID) -> list["User"]:
        stmt = (
            select(User)
            .join(
                UserConversationSecondary,
                User.id == UserConversationSecondary.user_id,
            )
            .where(UserConversationSecondary.conversation_id == conv_id)
        )
        res = await self._session.scalars(stmt)
        return list(res.all())

    async def get_conv_with_admin_info(self, conv_id: uuid.UUID) -> Conversation:
        stmt = (
            select(Conversation)
            .where(Conversation.id == conv_id)
            .options(joinedload(Conversation.user_admin))
        )
        conv = await self._session.scalar(stmt)
        return conv

    # may be it will be better to make it using one querie
    # this function do it with two queries using loaded messages and than selecting them
    async def get_conv_messages(self, conv_id: uuid.UUID) -> list["Message"]:
        conv = await self.get_conv_with_messages(conv_id)
        return conv.messages

    async def get_conv_with_messages(self, conv_id: uuid.UUID) -> Conversation:
        stmt = (
            select(Conversation)
            .where(Conversation.id == conv_id)
            .options(joinedload(Conversation.messages))
        )
        conv = await self._session.scalar(stmt)
        return conv

    async def create(self, data: dict) -> Conversation:
        new_conv = Conversation(**data)
        new_asoc = UserConversationSecondary(edit_permission=True)
        new_asoc.conversation_id = new_conv.id
        new_asoc.user_id = new_conv.user_admin_fk
        self._session.add(new_conv)
        await self._session.commit()
        return new_conv
