import os
# creats env var for test mode
os.environ["TEST_ENV"] = ".env.test"

import pytest
from typing import AsyncGenerator
from dotenv import load_dotenv
from httpx import AsyncClient, ASGITransport
from fastapi.testclient import TestClient
import asyncio
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
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session
import uuid
from asyncio import current_task
from src.models.base import Base
from src.models.chat_models import Conversation
from src.models.user_model import User
from src.schemas.conversation import AddUser, ConversationResponse
from src.schemas.users import User_on_request, CreateUser, User_on_response, UserInDB
import data_generator
from sqlalchemy import select
from typing import Callable
from src.dependencies.session_dependency import session_dep
from src.crud.conversation_repository import ConversationRepository
from src.crud.message_repository import MessageRepository
from src.crud.user_repository import UserRepository
from sqlalchemy.pool import NullPool
from models.utils import TestFullUser


DB_ENTIIIES_COUNTER = 10



   
    
@pytest.fixture(scope="session", autouse=True)
def create_migrations():
    print("Running migrations")
    os.system(f"alembic upgrade head")


@pytest.fixture(scope="session")
def engine():
    engine = create_async_engine(
        url=settings.db_settings.db_url,
        poolclass=NullPool,
    )
    yield engine
    engine.sync_engine.dispose()


@pytest.fixture(scope="session")
async def create(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.reflect)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
async def db_session(engine, create) -> AsyncSession:

    sessionmaker = async_sessionmaker(
        bind=engine, autoflush=False, autocommit=False, expire_on_commit=False
    )
    session = async_scoped_session(
        sessionmaker,
        scopefunc=current_task,
    )
    return session


@pytest.fixture(scope="session")
async def override_session_dep(db_session) -> AsyncSession:

    async def _override_session_dep():
        async with db_session() as ses:
            yield ses

    return _override_session_dep

@pytest.fixture(scope="function")
async def function_conv_request_model():
    model = data_generator.ConversationRequestFactory.build()
    return model

@pytest.fixture(scope="function")
async def override_get_current_user_auth(db_session):
    from src.authorization.dependency_auth import _get_auth_user
    from src.main import app
    original = _get_auth_user
    async def _override_get_current_user_auth():
        async with db_session() as session:
            model = data_generator.UserOnResponseFactory.build()
            user = User(**model.model_dump())
            db_session.add(user)
            await db_session.commit()
            yield user
            await db_session.delete(user)
            await db_session.commit()
    app.dependency_overrides[_get_auth_user] = _override_get_current_user_auth
    yield
    app.dependency_overrides[_get_auth_user] = original


@pytest.fixture(scope="session")
def session_main_dependencies_overriden_app(override_session_dep: Callable):
    from src.models import db_handler
    from src.main import app
    app.dependency_overrides[db_handler.session_dependency] = override_session_dep
    return app


@pytest.fixture(scope="session")
async def ac(session_main_dependencies_overriden_app):
    app = session_main_dependencies_overriden_app
    """Fixture to create a FastAPI test client."""
    # instead of app = app, use this to avoid the DeprecationWarning:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as async_test_client:
        yield async_test_client




@pytest.fixture(scope="function")
async def db_context_session(db_session):
    async with db_session() as ses:
        yield ses

@pytest.fixture(scope="function")
async def function_get_env_for_registration(db_context_session) -> CreateUser:
    model = data_generator.CreateUserFactory.build()
    yield model
    db_session = db_context_session
    created = await db_session.scalar(select(User).where(User.name == model.name))
    if created:
        await db_session.delete(created)
        await db_session.commit()



@pytest.fixture(scope="function")
async def function_create_user_for_test(
    db_context_session,
):
    model = data_generator.CreateUserFactory.build()
    db_session = db_context_session

    new_obj = User(**model.model_dump(exclude={"password_repeat"}))
    db_session.add(new_obj)
    await db_session.commit()

    yield TestFullUser(**new_obj.__dict__)

    entity = await db_session.get(User, new_obj.id)
    if entity:
        await db_session.delete(entity)
        await db_session.commit()
        

@pytest.fixture(scope="function")
async def function_create_conv_for_test(
    db_context_session,
):
    
    urepo= UserRepository(session=db_context_session)
    user = await urepo.create(data_generator.CreateUserFactory.build().model_dump(exclude={"password_repeat"}))
    repo = ConversationRepository(session=db_context_session)
    model = data_generator.ConversationRequestFactory.build().model_dump()
    model.update({"user_admin_fk": user.id})
    conv = await repo.create(model)
    db_session = db_context_session
    yield conv

    await db_context_session.delete(conv)
    await db_context_session.commit()
        
@pytest.fixture(scope="function")
async def function_create_add_user_schema(function_create_user_for_test):
    schema = AddUser(user_id = str(function_create_user_for_test.id), is_moder = False)
    yield schema


@pytest.fixture(scope="function")
async def function_get_update_schema():
    schema = data_generator.ConversationUpdateFactory.build()
    return schema

@pytest.fixture(scope="function")
async def function_update_shchema():
    return data_generator.UserforUpdateFactory.build()


@pytest.fixture(scope="function")
async def function_fill_db_for_many_users(db_context_session):
    db_session = db_context_session
    model_list = []
    for i in range(DB_ENTIIIES_COUNTER):
        model_list.append(data_generator.CreateUserFactory.build())

    users = []
    for entity in model_list:
        user = User(**entity.model_dump(exclude={"password_repeat"}))
        users.append(user)
        db_session.add(user)

    await db_session.commit()
    yield   
    for user in users:
        await db_session.delete(user)
    await db_session.commit()

