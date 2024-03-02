import uuid
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect

from routers import router as router_api_v1
from config import settings
from fastapi.responses import HTMLResponse

from src.authorization.dependency_auth import get_current_user
from src.connections.connection_manager import ManagersHandler
from src.dependencies.repo_providers_dependency import message_repo_provider

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
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
            // Get the conv_id from the URL
            var convId = window.location.pathname.split('/')[1];
            
            var ws = new WebSocket("ws://localhost:8000/" + convId + "/ws");
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

app = FastAPI()
app.include_router(
    router=router_api_v1,
    prefix=settings.router_settings.api_v1_prefix,
)

managers_handler = ManagersHandler()


# Testing
@app.get("/{conv_id}")
async def get():
    return HTMLResponse(html)


# Testing
@app.websocket("/{conv_id}/ws")
async def websocket_endpoint(conv_id: uuid.UUID, websocket: WebSocket, message_repo: message_repo_provider, ):
    manager = await managers_handler.get_manager(key=conv_id)
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = {
                "conversation_fk": conv_id,
                "content": data,
                "user_fk": "891eefdc-9271-4699-8915-dc2f6613e935",
            }
            await message_repo.create(message_data)
            await manager.broadcast(f"Clients #{manager.counter}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Clients #{manager.counter} left the chat")


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
