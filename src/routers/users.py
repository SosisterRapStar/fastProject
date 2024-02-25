import uuid
from typing import List
from fastapi import APIRouter
from sqlalchemy.exc import IntegrityError

from src.crud.exceptions import RecordNotFoundError
from src.dependencies.hash_dependency import (
    User_on_request_hash_dep,
    User_for_update_hash_dep,
)
from src.dependencies.repo_providers_dependency import user_repo_provider
from src.routers.errors import UserNotFoundError
from src.schemas.conversation import ConversationResponse
from src.schemas.users import User_on_response

router = APIRouter(tags=["Users"])


# TODO: чтобы каждый раз не создавать объект репозиториев вынести эту логику в отдельные классы


# @router.post(
#     "/",
#     response_model=User_on_response,
# )
# async def create_user(user: User_on_request_hash_dep, user_repo: user_repo_provider):
#     return await user_repo.create(user.model_dump())


@router.get(
    "/",
    response_model=List[User_on_response],
)
async def get_users(user_repo: user_repo_provider):
    return await user_repo.get()


@router.get(
    "by_name/{user_name}/",
    response_model=User_on_response,
)
async def get_user_by_name(user_name: str, user_repo: user_repo_provider):
    try:
        return await user_repo.get(name=user_name)
    except RecordNotFoundError:
        raise UserNotFoundError()


@router.get(
    "/{user_id}/",
    response_model=User_on_response,
)
async def get_user_by_id(user_id: uuid.UUID, user_repo: user_repo_provider):
    try:
        return await user_repo.get(id=user_id)
    except IntegrityError:
        raise UserNotFoundError()


@router.get(
    "/convs/{user_id}/",
    response_model=List[ConversationResponse],
)
async def get_user_convs_by_id(user_id: uuid.UUID, user_repo: user_repo_provider):
    try:
        return await user_repo.get_convs(user_id=user_id)
    except IntegrityError:
        raise UserNotFoundError()


# @router.patch(
#     "/{user_id}/",
#     response_model=User_on_response,
# )
# async def update_user_by_id(
#     user_repo: user_repo_provider,
#     user_id: uuid.UUID,
#     user: User_for_update_hash_dep,
# ):
#     try:
#         return await user_repo.update(user.model_dump(exclude_unset=True), id=user_id)
#     except IntegrityError:
#         raise UserNotFoundError()


# @router.patch(
#     "/by_name/{user_name}/",
#     response_model=User_on_response,
# )
# async def update_user_by_name(
#     user_repo: user_repo_provider,
#     user_name: str,
#     user: User_for_update_hash_dep,
# ):
#     try:
#         return await user_repo.update(
#             user.model_dump(exclude_unset=True), name=user_name
#         )
#     except IntegrityError:
#         raise UserNotFoundError()



@router.delete("/{user_id}/")
async def delete_user_by_id(
    user_repo: user_repo_provider,
    user_id: uuid.UUID,
):
    try:
        return await user_repo.delete(id=user_id)
    except IntegrityError:
        raise UserNotFoundError()
