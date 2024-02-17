from typing import Annotated

from fastapi import Depends

from src.crud.conversation_repository import ConversationRepository
from src.crud.message_repository import MessageRepository
from src.crud.user_repository import UserRepository
from src.dependencies.session_dependency import session_dep


async def get_user_repo(session: session_dep) -> UserRepository:
    return UserRepository(session=session)


async def get_conv_repo(session: session_dep) -> ConversationRepository:
    return ConversationRepository(session=session)


async def get_message_repo(session: session_dep) -> MessageRepository:
    return MessageRepository(session=session)

user_repo_provider = Annotated[UserRepository, Depends(get_user_repo)]
conv_repo_provider = Annotated[ConversationRepository, Depends(get_conv_repo)]
message_repo_provider = Annotated[MessageRepository, Depends(get_message_repo)]
