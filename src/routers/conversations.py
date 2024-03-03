import uuid
from typing import List
from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError, NoResultFound

from src.authorization.dependency_auth import get_current_user_id
from src.connections.connection_manager import ConnectionManagerIsNotEmptyError
from src.crud.exceptions import RecordNotFoundError, NoEditPermissionsError
from src.dependencies.repo_providers_dependency import conv_repo_provider
from src.main import managers_handler
from src.routers.errors import (
    UserAlreadyAddedError,
    ConversationNotFoundError,
    AdminUserNotFoundError, EditPermissionsError,
)
from src.schemas.conversation import (
    ConversationResponse,
    ConversationRequest,
    ConversationUpdate,
    AddUser,
)


from src.schemas.message import ResponseMessage
from src.schemas.users import User_on_response

router = APIRouter(tags=["Conversations"])


@router.get(
    "/",
    response_model=List[ConversationResponse],
)
async def get_all_conversations(conv_repo: conv_repo_provider):
    return await conv_repo.get()


@router.post(
    "/create/",
    response_model=ConversationResponse,
)
async def create_conversation(
    user_id: get_current_user_id,
    conv_repo: conv_repo_provider,
    conversation: ConversationRequest,
):
    conv_dict = conversation.model_dump()
    conv_dict.update({"user_admin_fk": user_id})

    return await conv_repo.create(conv_dict)


@router.get(
    "/users/{conv_id}/",
    response_model=List[User_on_response],
)
async def get_all_users_in_conv(conv_id: uuid.UUID, conv_repo: conv_repo_provider):
    try:
        return await conv_repo.get_users(conv_id=conv_id)
    except RecordNotFoundError:
        raise ConversationNotFoundError()


@router.get("/{conv_name}/", response_model=ConversationResponse)
async def get_conv_by_name(conv_name: str, conv_repo: conv_repo_provider):
    try:
        return await conv_repo.get(name=conv_name)
    except RecordNotFoundError:
        raise ConversationNotFoundError()


@router.get("/by_id/{conv_id}/", response_model=ConversationResponse)
async def get_conv_by_id(conv_id: uuid.UUID, conv_repo: conv_repo_provider):
    try:
        return await conv_repo.get(id=conv_id)
    except RecordNotFoundError:
        raise ConversationNotFoundError()


@router.patch(
    "/{conv_id}/",
    response_model=ConversationResponse,
)
async def update_conv_by_id(
    conv_id: uuid.UUID,
    conv_repo: conv_repo_provider,
    conversation: ConversationUpdate,
):
    try:
        return await conv_repo.update(
            conversation.model_dump(exclude_unset=True), id=conv_id
        )
    except NoResultFound:
        raise ConversationNotFoundError()


@router.patch(
    "/by_name/{conv_name}/",
    response_model=ConversationResponse,
)
async def update_conv_by_name(
    conv_name: str,
    conv_repo: conv_repo_provider,
    conversation: ConversationUpdate,
):
    try:
        return await conv_repo.update(
            conversation.model_dump(exclude_unset=True), name=conv_name
        )
    except NoResultFound:
        raise ConversationNotFoundError()


@router.post("users/{conv_id}/")
async def add_user_to_conversation(
    current_user: get_current_user_id,
    conv_id: uuid.UUID,
    conv_repo: conv_repo_provider,
    add_model: AddUser,
) -> None:

    try:
        await conv_repo.add_user(
            current_user=current_user,
            user_id=add_model.user_id,
            permission=add_model.is_moder,
            conv_id=conv_id,
        )
    except IntegrityError:
        raise UserAlreadyAddedError()
    except RecordNotFoundError:
        raise ConversationNotFoundError()
    except NoEditPermissionsError:
        raise EditPermissionsError()



@router.delete("/{conv_id}/")
async def delete_conv(conv_id: uuid.UUID, conv_repo: conv_repo_provider):
    try:
        await conv_repo.delete(id=conv_id)
        await managers_handler.delete_conv(conv_id)

    except RecordNotFoundError:
        raise ConversationNotFoundError()
    except NoEditPermissionsError:
        raise EditPermissionsError()


