from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from routers import router as router_api_v1
from config import router_settings

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     async with db_handler.engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#
#     yield


app = FastAPI()
app.include_router(
    router=router_api_v1,
    prefix=router_settings.api_v1_prefix,
)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
