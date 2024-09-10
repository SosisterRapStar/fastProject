from typing import Annotated
from fastapi import Depends
from src.services.connection_manager import ConnectionManager
from .repo_providers_dependency import conv_repo_provider
from .connection_dependencies import conv_managers_handler_provider
from src.services.connection_manager import ChatService

def get_chat_service(repo: conv_repo_provider, manager: conv_managers_handler_provider) -> ChatService:
    return ChatService(conv_repo=repo, manager=manager)


chat_service_provider = Annotated[ChatService, 
                                  Depends(get_chat_service)]

