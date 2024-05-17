import uuid
from abc import ABC, abstractmethod
from fastapi import WebSocket
from crud.repo_abstract import CRUDRepository
from typing import Callable
from starlette.websockets import WebSocketDisconnect
import contextvars
from crud.conversation_repository import ConversationRepository


class AbstractConnectionManagersHadler(ABC):
    @abstractmethod
    def get_manager(self, key: str) -> "ConnectionManager":
        raise NotImplementedError

    @abstractmethod
    def delete_manager(self, key: str):
        raise NotImplementedError




# class ConnectionManagerNotFoundError(Exception):
#     def __init__(self, *args):
#         if args:
#             self.message = args[0]
#         else:
#             self.message = None

#     # ok it should be useful idk :|
#     def __str__(self):
#         if self.message:
#             return f"{self.message}"
#         return f"There is no such manager"
class ConnectionWithUserNotFound(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None
    def __str__(self):
        if self.message:
            return f"{self.message}"
        return f"NoAnyConnectionsWithUser"


# class ConversationConnectionManagersHandler(AbstractConnectionManagersHadler):
#     # maybe it should do redis

#     __singletone = None

#     def __new__(cls, *args, **kwargs):
#         if cls.__singletone is None:
#             cls.__singletone = super().__new__(cls, *args, **kwargs)
#             cls.__managers = dict()
#         return cls.__singletone

#     def __init__(self):
#         pass
        
#     def get_all(self):
#         return self.__managers
        
    
#     async def is_conv_registered(self, key: str) -> bool:
#         return key in self.__managers
    
#     async def registrate_conv(self, key: str) -> "ConnectionManager":
#         manager = ConnectionManager()
#         self.__managers[key] = manager
#         return manager
    
#     async def get_manager(self, key: str, create_if_no: bool = True) -> "ConnectionManager":
#         if await self.is_conv_registered(key):
#             return self.__managers[key]
#         if create_if_no:
#             return await self.registrate_conv(key)
#         return None # WARNING
        
    
#     async def delete_manager(self, key: str, delete_if_not_empty: bool = False):
#         try:
#             manager: ConnectionManager = self.__managers[key]
#         except LookupError:
#             raise ConnectionManagerNotFoundError()

#         if not manager.is_empty:
#             if delete_if_not_empty:
#                 await manager.disconnect_all()
#             else:
#                 return ...
#         del self.__managers[key]
    
   

class ConnectionManager:
    __singletone = None
    
    def __new__(cls, *args, **kwargs):
        if cls.__singletone is None:
            cls.__singletone = super().__new__(cls, *args, **kwargs)
            cls.__users_websockets: dict[uuid.UUID, set[WebSocket]] = dict()
        return cls.__singletone
    
    def __init__(self):
        self.__counter = 0
        
        
    async def connect(self, user_id: uuid.UUID, websocket: WebSocket):
        await websocket.accept()
        self.__counter += 1
        
        if user_id not in self.__users_websockets:
            self.__users_websockets[user_id] = set()
        self.__users_websockets[user_id].add(websocket)
        
    async def send_to_users(self, users: list[uuid.UUID], message: str):
        for user_id in users:
            if user_id in self.__users_websockets:
                for websocket in self.__users_websockets[user_id]:
                    await websocket.send_text(message)
            

    async def disconnect(self, user_id: uuid.UUID, websocket: WebSocket):
        if user_id in self.__users_websockets:
            self.__users_websockets[user_id].remove(websocket)
            self.__counter -= 1
        else:
            raise ConnectionWithUserNotFound(f"NoAnyConnectionsWithUser {user_id=}")

    async def disconnect_all(self):
        for user in self.__users_websockets:
            for websocket in self.__users_websockets[user]:
                await websocket.close()
        self.__users_websockets.clear()

    # async def send(self, websocket: WebSocket, message: str):
    #     await websocket.send_text(message)

    async def broadcast(self, message: str):
        for user in self.__users_websockets:
            for websocket in self.__users_websockets[user]:
                await websocket.send_text(message)
            
    # def is_empty(self) -> bool:
    #     return self.__counter
    
class ChatService:
    __singletone = None
    
    def __new__(cls, conv_repo, manager, *args, **kwargs):
        if cls.__singletone is None:
            cls.__singletone = super().__new__(conv_repo, manager, cls, *args, **kwargs)
        return cls.__singletone
    
    def __init__(self, conv_repo: ConversationRepository, manager: ConnectionManager):
        self.conv_repo = conv_repo
        self.manager = manager
    
    async def handle_message_from_user(self, user_id: uuid.UUID, message: dict): # message может быть и json
        users_list = ConversationRepository.get_users(message['conv_id'], selectable="id") 
        self.manager.send_to_users(users=users_list)
    
    
    
    
        
        
    
            




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
        
        
    

