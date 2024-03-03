import uuid
from abc import ABC, abstractmethod
from fastapi import WebSocket


class AbstractConnectionManagersHadler(ABC):
    @abstractmethod
    def __new__(cls, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def get_manager(self, key: uuid.UUID | int | str) -> "ConnectionManager":
        raise NotImplementedError

    @abstractmethod
    def delete_manager(self, key: uuid.UUID | int | str):
        raise NotImplementedError


class ConnectionManagerIsNotEmptyError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    # ok it should be useful idk :|
    def __str__(self):
        if self.message:
            return f"{self.message}"
        return f"Can not delete manager. Connections list not empty."


class ConversationConnectionManagersHandler(AbstractConnectionManagersHadler):
    # maybe it should do redis

    __singletone = None

    def __new__(cls, *args, **kwargs):
        if cls.__singletone is None:
            cls.__singletone = super().__new__(cls, *args, **kwargs)
        return cls.__singletone

    def __init__(self):
        self.managers = dict()

    async def get_manager(self, key: uuid.UUID | int) -> "ConnectionManager":
        if key in self.managers:
            return self.managers[key]
        manager = ConnectionManager()
        self.managers[key] = manager
        return manager

    async def delete_manager(self, key: uuid.UUID | int):
        manager = self.managers[key]
        if manager.connections:
            raise ConnectionManagerIsNotEmptyError()
        self.managers.pop(key)


class ConnectionManager:

    def __init__(self):
        self.connections = list()
        self.counter = 0

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.counter += 1
        self.connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.connections.remove(websocket)
        self.counter -= 1

    async def send(self, websocket: WebSocket, message: str):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.connections:
            await connection.send_text(message)
