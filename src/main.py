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


@app.get("/{conv_id}")
async def get():
    return HTMLResponse(html)


@app.websocket("/{conv_id}/ws")
async def websocket_endpoint(conv_id: uuid.UUID, websocket: WebSocket):
    manager = await managers_handler.get_manager(key=conv_id)
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Clients #{manager.counter}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Clients #{manager.counter} left the chat")


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
