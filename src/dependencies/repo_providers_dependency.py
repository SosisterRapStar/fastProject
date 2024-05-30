from typing import Annotated

from fastapi import Depends

from src.crud.conversation_repository import AbstractConversationRepository, ConversationRepository
from src.crud.invite_repo import AbstractInviteRepository, InviteRepository
from src.crud.message_repository import MessageRepository
from src.crud.user_repository import AbstractUserRepository, UserRepository
from src.dependencies.session_dependency import session_dep



async def get_user_repo(session: session_dep) -> AbstractUserRepository:
    return UserRepository(session=session)


async def get_conv_repo(session: session_dep) -> AbstractConversationRepository:
    return ConversationRepository(session=session)


async def get_message_repo(session: session_dep) -> MessageRepository:
    return MessageRepository(session=session)


async def get_invite_repo(session: session_dep) -> AbstractInviteRepository:
    return InviteRepository(session=session)


user_repo_provider = Annotated[AbstractUserRepository, Depends(get_user_repo)]
conv_repo_provider = Annotated[AbstractConversationRepository, Depends(get_conv_repo)]
message_repo_provider = Annotated[MessageRepository, Depends(get_message_repo)]
invite_repo_provider = Annotated[AbstractInviteRepository, Depends(get_invite_repo)]
