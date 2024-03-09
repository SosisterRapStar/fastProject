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
from src.authorization.dependency_auth import get_current_user, get_current_user_ws
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
# from middlewares.auth_middleware import WebSocketAuthMiddleware

middleware = [Middleware(ASGIMiddleware)]


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


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, log_config=config)
