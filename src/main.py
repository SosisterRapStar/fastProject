from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from routers import router as router_api_v1
from config import settings


app = FastAPI()
app.include_router(
    router=router_api_v1,
    prefix=settings.router_settings.api_v1_prefix,
)



if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
