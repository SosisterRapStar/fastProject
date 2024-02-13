from select import select

from src.crud.repo_abstract import CRUDAlchemyRepository
from src.models.chat_models import Conversation, UserConversationSecondary
from src.models.user_model import User


class UserRepository(CRUDAlchemyRepository):
    model = User

    async def get_user_with_convs(self, user_id) -> list[Conversation]:
        stmt = (
            select(Conversation)
            .join(User, User.id == UserConversationSecondary.user_id)
            .join(Conversation, Conversation.id == UserConversationSecondary.conversation_id)
            .where(User.id == user_id)
        )
        convs = await self.session.scalars(stmt)
        return list(convs.all())