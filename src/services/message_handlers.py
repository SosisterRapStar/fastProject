
from schemas.message import MessageForResponse
from dependencies.connection_dependencies import conv_managers_handler_provider
import uuid 
async def chat_message_handler(message: str):
    
    conv_managers_handler = conv_managers_handler_provider()
    response = message["data"]
    conv_id = message['channel']
    print(message)
    print(f"Handler {conv_managers_handler.get_all()}")
    manager = await conv_managers_handler.get_manager(key=conv_id)   
    if manager:
        print(f"Handler {manager.get_all()}")
        await manager.broadcast(response)
   
    