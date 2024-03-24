from typing import AsyncGenerator
import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from src.main import app
import asyncio
from src.config import settings
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    async_scoped_session,
    AsyncSession,
)

import os

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import Mapped, as_declarative
from src.config import settings
from typing import Annotated
import docker
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import db_handler

# session_dep = Annotated[AsyncSession, Depends(db_handler.session_dependency)]

# compose_file_path = '/home/vanya/'
# client = docker.from_env()

DOCKER_COMPOSE_FILE = "docker-compose-test.yaml"
client = docker.from_env()


engine = create_async_engine(
            url=settings.db_settings.db_url,
        )

session = async_sessionmaker(
    bind=engine, autoflush=False, autocommit=False, expire_on_commit=False
)

async def override_session_dep() -> AsyncSession:
    global session
    async with session() as ses:
        yield ses
        
app.dependency_overrides[db_handler.session_dependency] = override_session_dep


@pytest.fixture(scope="session", autouse=True)
def up_db():
    print("Start DB for tests")
    client.compose.up(detach=True, file=DOCKER_COMPOSE_FILE)
    
    yield
    
    print("Stop DB")
    client.compose.down(file=DOCKER_COMPOSE_FILE)

@pytest.fixture(scope="session", autouse=True)
def create_migrations():
    print("Running migrations")
    os.system(f'alembic upgrade head')
    

# @pytest.fixture(scope="session")
# async def ses():
#     global session
#     async with session() as ses:
#         yield ses
        
  
    
@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# @pytest.fixture(scope="session")
# def client() -> TestClient:
#     return TestClient(app)
    