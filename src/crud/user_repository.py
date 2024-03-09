import uuid
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from src.crud.repo_abstract import CRUDAlchemyRepository
from src.models.chat_models import Conversation, UserConversationSecondary
from src.models.user_model import User


class UserRepository(CRUDAlchemyRepository):
    _model = User

    # TODO: do something with session identity map for caching
    # TODO: errors handling

    async def get_convs(self, user_id: uuid.UUID) -> list["Conversation"]:
        stmt = (
            select(Conversation)
            .join(
                UserConversationSecondary,
                Conversation.id == UserConversationSecondary.conversation_id,
            )
            .where(UserConversationSecondary.user_id == user_id)
        )
        res = await self._session.scalars(stmt)
        return list(res.all())

    async def get_user_messages(self, user_id: uuid.UUID):
        user = await self.get_user_with_messages(user_id)
        return user.messages

    async def get_user_with_messages(self, user_id: uuid.UUID) -> User:
        stmt = select(User).where(User.id == user_id).options(joinedload(User.messages))
        user = await self._session.scalar(stmt)
        return user
