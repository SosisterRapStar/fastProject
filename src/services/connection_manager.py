import uuid
from abc import ABC, abstractmethod
from fastapi import WebSocket
from crud.repo_abstract import CRUDRepository
from typing import Callable
from starlette.websockets import WebSocketDisconnect
import contextvars
from crud.conversation_repository import ConversationRepository
from typing import TYPE_CHECKING
from .logger import log
import sys

if TYPE_CHECKING:
    from schemas.message import MessageFromBroker

class AbstractConnectionManagersHadler(ABC):
    @abstractmethod
    def get_manager(self, key: str) -> "ConnectionManager":
        raise NotImplementedError

    @abstractmethod
    def delete_manager(self, key: str):
        raise NotImplementedError


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

    
class ChatService:
    __singletone = None
    
    def __new__(cls, conv_repo, manager, *args, **kwargs):
        if cls.__singletone is None:
            cls.__singletone = super().__new__(cls, *args, **kwargs)
        return cls.__singletone
    
    def __init__(self, conv_repo: ConversationRepository, manager: "ConnectionManager"):
        self.conv_repo = conv_repo
        self.manager = manager
    
    async def handle_message_from_user(self, message: "MessageFromBroker"): # message может быть и json
        users_list = await self.conv_repo.get_users(conv_id=message.conversation_id, selectable="id") 
        await self.manager.send_to_users(users=users_list, message=message.content)

   

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
        log.debug(f"dict_size={sys.getsizeof(self.__users_websockets)}")
        log.debug(f"{user_id=} start connecting")
        await websocket.accept()
        self.__counter += 1
        
        log.debug(f"{user_id=} connected")
        
        if user_id not in self.__users_websockets:
            self.__users_websockets[user_id] = set()
        self.__users_websockets[user_id].add(websocket)
        
    async def send_to_users(self, users: list[uuid.UUID], message: str):
        for user_id in users:
            if user_id in self.__users_websockets:
                for websocket in self.__users_websockets[user_id]:
                    await websocket.send_json(message)
            

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

    
    
    
        
        
    

