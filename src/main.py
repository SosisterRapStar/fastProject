from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from routers import router as router_api_v1
from config import router_settings
from authorization import router as auth_router
from starlette.middleware.authentication import AuthenticationMiddleware
from authorization.security import JWTAuth


app = FastAPI()
app.include_router(
    router=router_api_v1,
    prefix=router_settings.api_v1_prefix,
)
app.include_router(
    router=auth_router,
    prefix=router_settings.api_v1_prefix,
)

app.add_middleware(AuthenticationMiddleware, backend=JWTAuth())

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
