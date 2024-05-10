from src.services.connection_manager import ConversationConnectionManagersHandler
from src.services.redis_service import RedisManager
from typing import Annotated
from fastapi import Depends


def get_conversation_connection_manager() -> ConversationConnectionManagersHandler:
    return ConversationConnectionManagersHandler()


conv_managers_handler_provider = Annotated[ConversationConnectionManagersHandler, 
                                  Depends(get_conversation_connection_manager)]

