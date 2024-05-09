
from schemas.message import MessageForResponse
from services.connection_manager import ConversationConnectionManagersHandler
import uuid 

async def chat_message_handler(message: str):
    conv_managers_handler = ConversationConnectionManagersHandler()
    response = message["data"]
    conv_id = message['channel']
    print(id(conv_managers_handler))
    
    # возможно нужно будет поменять эту логику и хранить в качетсве ключа в словаре не uuid а строку 
    print(await conv_managers_handler.get_all())
    manager = await conv_managers_handler.get_manager(key=conv_id)   
    if manager:
        print("saas")
        await manager.broadcast(response)
   
    