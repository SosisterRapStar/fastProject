from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from src.models import db_handler


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     async with db_handler.engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#
#     yield


app = FastAPI()


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
