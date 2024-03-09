import logging
import uuid
from typing import Annotated

import uvicorn
from fastapi import FastAPI, WebSocket, Header
from starlette.websockets import WebSocketDisconnect

from routers import router as router_api_v1
from config import settings
from fastapi.responses import HTMLResponse
from logger import setup_logging
from src.authorization.dependency_auth import get_current_user
from src.connections.connection_manager import (
    ConversationConnectionManagersHandler,
    conv_managers_handler,
)
from src.dependencies.repo_providers_dependency import (
    message_repo_provider,
    conv_repo_provider,
)
from starlette.middleware import Middleware
from middlewares.log_middleware import ASGIMiddleware
from middlewares.auth_middleware import WebSocketAuthMiddleware

middleware = [Middleware(ASGIMiddleware), Middleware(WebSocketAuthMiddleware)]

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

config = setup_logging()
log = logging.getLogger("__name__")

logging.getLogger("sqlalchemy.orm").setLevel(logging.ERROR)
logging.getLogger("sqlalchemy.engine").setLevel(logging.ERROR)
logging.getLogger("sqlalchemy.dialects").setLevel(logging.ERROR)

app = FastAPI(middleware=middleware)
app.include_router(
    router=router_api_v1,
    prefix=settings.router_settings.api_v1_prefix,
)


# Testing
@app.get("/{conv_id}")
async def get(
    current_user: get_current_user,
    conv_id: uuid.UUID,
    conv_repo: conv_repo_provider,
):
    # await conv_repo.get_conv_messages(conv_id=conv_id)
    return HTMLResponse(html)


# Testing. Acces_token header added for testing in /docs
@app.websocket("/{conv_id}/ws")
async def websocket_endpoint(
    conv_id: uuid.UUID,
    websocket: WebSocket,
    message_repo: message_repo_provider,
):
    manager = await conv_managers_handler.get_manager(key=conv_id)
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = {
                "conversation_fk": conv_id,
                "content": data,
                "user_fk": websocket.scope.get("user_id"),
            }
            await message_repo.create(message_data)
            await manager.broadcast(f"Clients {websocket.scope.get('user_id')}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(
            f"Clients {websocket.scope.get('user_id')}: left the chat"
        )


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, log_config=config)
