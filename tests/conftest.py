from enum import auto
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

from sqlalchemy import MetaData

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
from src.models.base import Base


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
def create_migrations():
    global metadata
    print("Running migrations")
    os.system(f'alembic upgrade head')
   
@pytest.fixture(scope="session")
def sync_client():
    tc = TestClient(app)
    return tc


@pytest.fixture(scope="session", autouse=True)
async def delete_all():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.reflect)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
   
    
    
        
        
@pytest.fixture(scope='session')
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()
    
@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# @pytest.fixture(scope="session")
# def client() -> TestClient:
#     return TestClient(app)
    