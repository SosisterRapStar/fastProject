from typing import Annotated
from fastapi import Depends
from src.services.connection_manager import ConnectionManager

def get_conversation_connection_manager() -> ConnectionManager:
    return ConnectionManager()


conv_managers_handler_provider = Annotated[ConnectionManager, 
                                  Depends(get_conversation_connection_manager)]

