import uuid
from typing import List

from fastapi import APIRouter
from sqlalchemy.exc import NoResultFound
from starlette import status

from src.authorization.dependency_auth import get_current_user_id
from src.dependencies.repo_providers_dependency import (
    user_repo_provider,
    message_repo_provider,
    conv_repo_provider,
)
from src.routers.errors import ConversationNotFoundError
from src.schemas.message import RequestMessage, ResponseMessage, UpdateMessage, ResponseWithUserMessage

router = APIRouter(tags=["Messages"])


@router.get(
    "/my",
    status_code=status.HTTP_200_OK,
    response_model=List[ResponseMessage],
)
async def get_user_messages(user_id: get_current_user_id, repo: user_repo_provider):
    return await repo.get_user_messages(user_id)


@router.post(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=ResponseMessage,
)
async def create_message(
    message: RequestMessage,
    user_id: get_current_user_id,
    message_repo: message_repo_provider,
):
    model_dict = message.model_dump()
    model_dict.update({"user_fk": user_id})
    return await message_repo.create(model_dict)


# user_id: get_current_user_id


@router.delete(
    "/{message_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_message(message_id: uuid.UUID, message_repo: message_repo_provider):
    return await message_repo.delete(id=message_id)


@router.patch(
    "/{message_id}", status_code=status.HTTP_200_OK, response_model=ResponseMessage
)
async def edit_message(
    message_id: uuid.UUID, message: UpdateMessage, message_repo: message_repo_provider
):
    return await message_repo.update(
        message.model_dump(exclude_unset=True), id=message_id
    )


@router.get(
    "/conv/{conv_id}",
    status_code=status.HTTP_200_OK,
    response_model=List[ResponseWithUserMessage],
)
async def get_conv_messages(conv_id: uuid.UUID, conv_repo: conv_repo_provider):
    try:
        return await conv_repo.get_conv_messages(conv_id=conv_id)
    except NoResultFound:
        raise ConversationNotFoundError()
