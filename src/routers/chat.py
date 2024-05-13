import uuid
from schemas.message import MessageToDb, MessageForResponse
from fastapi import APIRouter, WebSocket
from starlette.responses import HTMLResponse
from starlette.websockets import WebSocketDisconnect
from dependencies.broker_dependency import broker_provider 
from src.authorization.dependency_auth import get_current_user, get_current_user_ws
from src.dependencies.repo_providers_dependency import conv_repo_provider, message_repo_provider
from dependencies.connection_dependencies import conv_managers_handler_provider
from services.message_handlers import chat_message_handler
from .logger import log
import asyncio
router = APIRouter(
    tags=["chat"],
    responses={404: {"detai": "Not found"}},
)





html = """
<!DOCTYPE html>
<html>
<head>
    <title>Chat</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/websocket-client/1.2.0/websocket.min.js"></script>
</head>
<body>
<h1>WebSocket Chat</h1>
<form action="" onsubmit="sendMessage(event)">
    <input type="text" id="messageText" autocomplete="off"/>
    <button>Send</button>
</form>
<ul id='messages'>
</ul>
<script>
    var convId = window.location.pathname.split('/')[1];
      // Replace with your actual access token
    var ws = new WebSocket("ws://localhost:8000/" + convId + "/ws");
    ws.onopen = function(event) {
        ws.send(JSON.stringify({ 'Authorization': 'Bearer ' + token }));
    };
    ws.onmessage = function(event) {
        var messages = document.getElementById('messages')
        var message = document.createElement('li')
        var content = document.createTextNode(event.data)
        message.appendChild(content)
        messages.appendChild(message)
    };
    function sendMessage(event) {
        var input = document.getElementById("messageText")
        ws.send(input.value)
        input.value = ''
        event.preventDefault()
    }
</script>
</body>
</html>
"""



@router.get("/{conv_id}")
async def get(
    current_user: get_current_user,
    conv_id: uuid.UUID,
    conv_repo: conv_repo_provider,
    conv_managers_handler: conv_managers_handler_provider,
    broker: broker_provider,
):
    
    return HTMLResponse(html)


@router.websocket("/ws/{conv_id}")
async def websocket_endpoint(
    current_user: get_current_user_ws,
    conv_id: uuid.UUID,
    websocket: WebSocket,
    message_repo: message_repo_provider,
    conv_managers_handler: conv_managers_handler_provider,
    broker: broker_provider, 
):
    
    if not await conv_managers_handler.is_conv_registered(key=str(conv_id)):
        manager = await conv_managers_handler.registrate_conv(key=str(conv_id))
        await broker.subscribe(channel=str(conv_id), handler=chat_message_handler)
    else:
        manager = await conv_managers_handler.get_manager(key=str(conv_id))
    # a = await conv_managers_handler.get_all()
    await manager.connect(websocket)
    
    print(f"In chat {manager.get_all()}")
    
    try:
        while True:
            data = await websocket.receive_text()
            
            messageToSaveInDb = MessageToDb(conversation_fk=conv_id, 
                                   content=data, 
                                   user_fk=current_user.id,)
            
            await message_repo.create(messageToSaveInDb.model_dump())
            
            # вынести в отдельную функцию 
            messageForUsersAndOtherServers = \
            f"""
            user_name: {current_user.name},
            data: {data}
            """
            
            await broker.publish(channel=str(conv_id), message=messageForUsersAndOtherServers)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(
            f"Clients {current_user.name}: left the chat"
        )
        await conv_managers_handler.delete_manager(key=str(conv_id))
