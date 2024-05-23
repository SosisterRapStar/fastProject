import uuid

from fastapi import APIRouter, WebSocket
from dependencies.broker_dependency import broker_provider
from src.authorization.dependency_auth import get_current_user, get_current_user_ws
from src.dependencies.repo_providers_dependency import (
    conv_repo_provider,
    message_repo_provider,
)
from dependencies.connection_dependencies import conv_managers_handler_provider
from services.message_handlers import chat_message_handler
from src.dependencies.chat_service_dependency import chat_service_provider
from .logger import log
import asyncio
from src.services.websocket_server import start_server

router = APIRouter(
    tags=["chat"],
    responses={404: {"detai": "Not found"}},
)
import sys


# html = """
# <!DOCTYPE html>
# <html>
# <head>
#     <title>Chat</title>
#     <script src="https://cdnjs.cloudflare.com/ajax/libs/websocket-client/1.2.0/websocket.min.js"></script>
# </head>
# <body>
# <h1>WebSocket Chat</h1>
# <form action="" onsubmit="sendMessage(event)">
#     <input type="text" id="messageText" autocomplete="off"/>
#     <button>Send</button>
# </form>
# <ul id='messages'>
# </ul>
# <script>
#     var convId = window.location.pathname.split('/')[1];
#       // Replace with your actual access token
#     var ws = new WebSocket("ws://localhost:8000/" + convId + "/ws");
#     ws.onopen = function(event) {
#         ws.send(JSON.stringify({ 'Authorization': 'Bearer ' + token }));
#     };
#     ws.onmessage = function(event) {
#         var messages = document.getElementById('messages')
#         var message = document.createElement('li')
#         var content = document.createTextNode(event.data)
#         message.appendChild(content)
#         messages.appendChild(message)
#     };
#     function sendMessage(event) {
#         var input = document.getElementById("messageText")
#         ws.send(input.value)
#         input.value = ''
#         event.preventDefault()
#     }
# </script>
# </body>
# </html>
# """


@router.get("/{conv_id}")
async def get(
    current_user: get_current_user,
    conv_id: uuid.UUID,
    conv_repo: conv_repo_provider,
    conv_managers_handler: conv_managers_handler_provider,
    broker: broker_provider,
):

    pass


@router.websocket("/ws/")
async def websocket_endpoint(
    current_user: get_current_user_ws,
    websocket: WebSocket,
    manager: conv_managers_handler_provider,
    broker: broker_provider,
    chat: chat_service_provider,
):
    
    await manager.connect(user_id=current_user.id, websocket=websocket)

    server = asyncio.create_task(start_server(
        manager=manager,
        websocket=websocket,
        current_user=current_user,
        broker=broker,
        chat=chat,
        )
        
    )
    
