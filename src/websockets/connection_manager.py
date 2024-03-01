# from typing import Annotated
#
# from fastapi import Depends
# from fastapi import WebSocket
#
#
# class ConnectionManager:
#     __singletone = None
#
#     def __new__(cls, *args, **kwargs):
#         if cls.__singletone is None:
#             cls.__singletone = super().__new__(cls, *args, **kwargs)
#         return cls.__singletone
#
#     def __init__(self):
#         self.connections = list()
#
#     async def connect(self, websocket: WebSocket):
#         await websocket.accept()
#         self.connections.append(websocket)
#
#     def disconnect(self, websocket: WebSocket):
#         self.connections.remove(websocket)
#
#     async def send(self, websocket: WebSocket, message: str):
#         await websocket.send_text(message)
#
#     async def broadcasdcast(self, message: str):
#         for connection in self.connections:
#             await connection.send_text(message)
#
#
# async def get_connection_manager() -> ConnectionManager:
#     return ConnectionManager()
#
#
# connection_manager = Annotated[
#     ConnectionManager, Depends(get_connection_manager)
# ]
