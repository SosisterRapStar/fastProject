
from schemas.message import MessageForResponse
from dependencies.connection_dependencies import conv_managers_handler_provider
import uuid 
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .connection_manager import ChatService
    
from src.schemas.message import MessageFromBroker

async def chat_message_handler(message: str, chat: "ChatService"):
    message = MessageFromBroker.model_validate_json(message['data'])
    await chat.handle_message_from_user(message)
    
   
    
   
    