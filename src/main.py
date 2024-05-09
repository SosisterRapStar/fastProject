
import uvicorn
import logging
from fastapi import FastAPI, WebSocket
from src.routers import router as router_api_v1
from src.config import settings
from fastapi.responses import HTMLResponse
from starlette.middleware import Middleware
from src.middlewares.log_middleware import ASGIMiddleware


middleware = [Middleware(ASGIMiddleware)]




logging.getLogger("sqlalchemy.orm").setLevel(logging.ERROR)
logging.getLogger("sqlalchemy.engine").setLevel(logging.ERROR)

app = FastAPI(middleware=middleware)

app.include_router(
    router=router_api_v1,
    prefix=settings.router_settings.api_v1_prefix,
)


