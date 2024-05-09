import uuid
from abc import ABC, abstractmethod
from fastapi import WebSocket
from crud.repo_abstract import CRUDRepository
from typing import Callable
from starlette.websockets import WebSocketDisconnect
import contextvars


class AbstractConnectionManagersHadler(ABC):
    @abstractmethod
    def get_manager(self, key: str) -> "ConnectionManager":
        raise NotImplementedError

    @abstractmethod
    def delete_manager(self, key: str):
        raise NotImplementedError



class ConnectionManagerNotFoundError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    # ok it should be useful idk :|
    def __str__(self):
        if self.message:
            return f"{self.message}"
        return f"There is no such manager"


class ConversationConnectionManagersHandler(AbstractConnectionManagersHadler):
    # maybe it should do redis

    __singletone = None

    def __new__(cls, *args, **kwargs):
        if cls.__singletone is None:
            cls.__singletone = super().__new__(cls, *args, **kwargs)
            cls.__managers = dict()
        return cls.__singletone

    def __init__(self):
        pass
        
    async def get_all(self):
        return self.__managers
        
    
    async def is_conv_registered(self, key: str) -> bool:
        return key in self.__managers
    
    async def registrate_conv(self, key: str) -> "ConnectionManager":
        manager = ConnectionManager()
        self.__managers[key] = manager
        return manager
    
    async def get_manager(self, key: str, create_if_no: bool = True) -> "ConnectionManager":
        if await self.is_conv_registered(key):
            return self.__managers[key]
        if create_if_no:
            return await self.registrate_conv(key)
        return None # WARNING
        
    
    async def delete_manager(self, key: str, delete_if_not_empty: bool = False):
        try:
            manager: ConnectionManager = self.__managers[key]
        except LookupError:
            raise ConnectionManagerNotFoundError()

        if not manager.is_empty:
            if delete_if_not_empty:
                await manager.disconnect_all()
            else:
                return ...
        del self.__managers[key]
    
   

class ConnectionManager:

    def __init__(self):
        self.__connections: list[WebSocket] = list()
        self.__counter = 0
        

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.__counter += 1
        self.__connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.__connections.remove(websocket)
        self.__counter -= 1

    async def disconnect_all(self):
        for socket in self.__connections:
            await socket.close()
        self.__connections.clear()

    async def send(self, websocket: WebSocket, message: str):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        print(self.__connections)
        for connection in self.__connections:
            await connection.send_text(message)
            
    def is_empty(self) -> bool:
        return self.__counter
            




# class WebsocketListener:
    
   
#     def __init__ (self, websocket: WebSocket, manager: ConnectionManager, repo: CRUDRepository) -> None:
#         self.websocket = websocket
#         self.manager = manager
#         self.repo = repo
    
#     async def __listen(self, message_handler: Callable, **kwargs):
#         try:
#             while True:
#                 data = await self.websocket.receive_text()
                
               
                
#                 messageForUsersAndOtherServers = \
#                 f"""
#                 user_name: {current_user.name},
#                 data: {data}
#                 """
#                 await manager.broadcast(f"Clients {current_user.name}: {data}")
            
#         except WebSocketDisconnect:
#             self.manager.disconnect(websocket)
#             await manager.broadcast(
#                 f"Clients {current_user.name}: left the chat"
#             )
        
        
    

