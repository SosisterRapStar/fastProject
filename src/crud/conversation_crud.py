from sqlalchemy.ext.asyncio import async_sessionmaker
from src.models.base import db_handler
from src.models.chat_models import Conversation
from src.models.user_model import User
from src.schemas.conversation import ConversationRequest


# def create_conversation(
#     async_session: async_sessionmaker,
#     user: User,
#     conversation_shema: ConversationRequest,
# ):
#     new_conv = Conversation(**ConversationRequest.model_dump(),
#                             user_admin_fk=user.id,
#                             )


def delete_conversation(async_session: async_sessionmaker):
    pass


def update_conversation(async_session: async_sessionmaker):
    pass
