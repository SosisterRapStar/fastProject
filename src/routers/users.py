import uuid
from typing import List
from fastapi import APIRouter
from sqlalchemy.exc import IntegrityError
from starlette import status
from starlette.responses import JSONResponse

from src.authorization.dependency_auth import get_current_user, get_current_user_id
from src.crud.exceptions import RecordNotFoundError
from src.dependencies.dependency_hash import (
    password_hash_dependency,
    update_hash_dependency,
)
from src.dependencies.repo_providers_dependency import user_repo_provider
from src.routers.errors import UserNotFoundError
from src.schemas.conversation import ConversationResponse
from src.schemas.users import User_on_response
from logger import log
router = APIRouter(tags=["Users"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def create_user(user: password_hash_dependency, repo: user_repo_provider):

    user = await repo.create(user.model_dump(exclude={"password_repeat"}))

    log.debug(f"New user registeredm id {user.id}")

    payload = {"message": "Man YOO have just created a user account"}
    return JSONResponse(content=payload)


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=User_on_response,
)
async def get_curr_user(user: get_current_user):

    return user


#
@router.patch(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=User_on_response,
)
async def update_curr_user(
    user: get_current_user,
    update_schema: update_hash_dependency,
    user_repo: user_repo_provider,
):
    return await user_repo.update(
        data=update_schema.model_dump(exclude_unset=True),
        model_object=user,
    )


@router.get(
    "/",
    response_model=List[User_on_response],
    status_code=status.HTTP_200_OK,
)
async def get_users(user_repo: user_repo_provider):

    log.debug("")
    return await user_repo.get()


@router.get(
    "by_name/{user_name}/",
    response_model=User_on_response,
    status_code=status.HTTP_200_OK,
)
async def get_user_by_name(user_name: str, user_repo: user_repo_provider):
    try:
        log.debug("")
        return await user_repo.get(name=user_name)
    except RecordNotFoundError:
        log.error("")
        raise UserNotFoundError()


# @router.get(
#     "/{user_id}/",
#     response_model=User_on_response,
# )
# async def get_user_by_id(user_id: uuid.UUID, user_repo: user_repo_provider):
#     try:
#         return await user_repo.get(id=user_id)
#     except IntegrityError:
#         raise UserNotFoundError()


@router.get(
    "/convs/",
    response_model=List[ConversationResponse],
)
async def get_user_convs(
    user_id: get_current_user_id, user_repo: user_repo_provider
):
    try:
        return await user_repo.get_convs(user_id=user_id)
    except IntegrityError:
        raise UserNotFoundError()


@router.delete("/{user_ id}/")
async def delete_user_by_id(
    user_repo: user_repo_provider,
    user_id: uuid.UUID,
):
    try:
        return await user_repo.delete(id=user_id)
    except IntegrityError:
        raise UserNotFoundError()
