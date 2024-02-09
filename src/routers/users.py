import uuid
from typing import List, Annotated
from fastapi import APIRouter, Path, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.user_crud import load_user_with_convs
from src.dependencies.get_dependency import get_by_id_dep, get_by_name
from src.dependencies.hash_dependency import User_on_request_hash_dep
from src.dependencies.session_dependency import session_dep
from src.schemas.user_conversation import UserOnResponseWithConvs

from src.schemas.users import User_on_response, User_on_request
from src.crud import user_crud

router = APIRouter(tags=["Users"])


@router.post(
    "/",
    response_model=User_on_response,
)
async def create_user(user: User_on_request_hash_dep, session: session_dep):
    return await user_crud.create_user(async_session=session, user=user)


@router.get(
    "/",
    tags=["users"],
    response_model=List[User_on_response],
)
async def get_users(session: session_dep):
    return await user_crud.get_users(async_session=session)

@router.get(
    "by_name/{user_name}/",
    response_model=User_on_response,
)
async def get_user_by_name(user: get_by_name):
    return user


@router.get(
    "/{user_id}/",
    tags=["user"],
    response_model=User_on_response,
)
async def get_user_by_id(user: get_by_id_dep):
    return user

@router.get(
    "/convs/{user_id}/",
    response_model=UserOnResponseWithConvs,
)
async def get_user_by_id(user_id: uuid.UUID, session: session_dep):
    return await load_user_with_convs(user_id=user_id, async_session=session)


@router.patch("/{user_id}/", response_model=User_on_response)
async def update_user_by_id(
        user_db: get_by_id_dep,
        session: session_dep,
        user: User_on_request_hash_dep,
):
    return await user_crud.update_user(
        async_session=session,
        user_db=user_db,
        user_update=user,
    )
