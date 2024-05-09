
from schemas.message import MessageForResponse
from .connection_manager import conv_managers_handler
import uuid 

async def chat_message_handler(message: str):
    response = message["data"]
    conv_id = message['channel']
    # возможно нужно будет поменять эту логику и хранить в качетсве ключа в словаре не uuid а строку 
    conv_id = uuid.UUID(conv_id).hex
    manager = await conv_managers_handler.get_manager(conv_id=conv_id, create_if_no=False)   
    if manager:
        manager.broadcast(response)
    
    