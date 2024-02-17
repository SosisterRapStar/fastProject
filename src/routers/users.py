import uuid
from typing import List, Annotated
from fastapi import APIRouter, Path, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.user_repository import UserRepository
from src.dependencies.get_dependency import get_by_id_dep, get_by_name
from src.dependencies.hash_dependency import User_on_request_hash_dep
from src.dependencies.session_dependency import session_dep
from src.schemas.conversation import ConversationResponse
from src.schemas.user_conversation import UserOnResponseWithConvs
from src.schemas.users import User_on_response, User_on_request


router = APIRouter(tags=["Users"])

#TODO: чтобы каждый раз не создавать объект репозиториев вынести эту логику в отдельные классы

@router.post(
    "/",
    response_model=User_on_response,
)
async def create_user(user: User_on_request_hash_dep, session: session_dep):
    user_repo = UserRepository(session=session)
    return await user_repo.create(user.model_dump())


@router.get(
    "/",
    tags=["users"],
    response_model=List[User_on_response],
)
async def get_users(session: session_dep):
    user_repo = UserRepository(session=session)
    return await user_repo.get()

@router.get(
    "by_name/{user_name}/",
    response_model=User_on_response,
)
async def get_user_by_name(user_name: str, session: session_dep):
    user_repo = UserRepository(session=session)
    return await user_repo.get(name=user_name)



@router.get(
    "/{user_id}/",
    tags=["user"],
    response_model=User_on_response,
)
async def get_user_by_id(user_id: uuid.UUID, session: session_dep):
    user_repo = UserRepository(session=session)
    return await user_repo.get(id=user_id)

@router.get(
    "/convs/{user_id}/",
    response_model=ConversationResponse,
)
async def get_user_convs_by_id(user_id: uuid.UUID, session: session_dep):
    user_repo = UserRepository(session=session)
    return await user_repo.get_convs(user_id=user_id)


@router.patch("/{user_id}/", response_model=User_on_response)
async def update_user_by_id(
        session: session_dep,
        user_id: uuid.UUID,
        user: User_on_request_hash_dep,
):
    user_repo = UserRepository(session=session)
    return await user_repo.update(user.model_dump(exclude_unset=True), id=user_id)
