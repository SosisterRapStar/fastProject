import uuid
from typing import List
from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError
from src.dependencies.repo_providers_dependency import conv_repo_provider
from src.schemas.conversation import (
    ConversationResponse,
    ConversationRequest,
    ConversationUpdate,
    AddUser,
)
from src.schemas.user_conversation import ConversationWithUsersResp

from src.schemas.users import User_on_response, User_on_request

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
    conv_repo: conv_repo_provider, conversation: ConversationRequest
):

    try:
        return await conv_repo.create(conversation.model_dump())
    except IntegrityError:
        raise HTTPException(status_code=404, detail="Admin user not found")


@router.get(
    "/users/{conv_id}/",
    response_model=List[User_on_response],
)
async def get_all_users_in_conv(conv_id: uuid.UUID, conv_repo: conv_repo_provider):

    try:
        return await conv_repo.get_users(conv_id=conv_id)
    except IntegrityError:
        raise HTTPException(status_code=404, detail="Conversation not found")


@router.get("/{conv_name}/", response_model=ConversationResponse)
async def get_conv_by_name(conv_name: str, conv_repo: conv_repo_provider):

    try:
        return await conv_repo.get(name=conv_name)
    except IntegrityError:
        raise HTTPException(status_code=404, detail="Conversation not found")


@router.get("/by_id/{conv_id}/", response_model=ConversationResponse)
async def get_conv_by_id(conv_id: uuid.UUID, conv_repo: conv_repo_provider):

    try:
        return await conv_repo.get(id=conv_id)
    except IntegrityError:
        raise HTTPException(status_code=404, detail="Conversation not found")


@router.patch(
    "/{conv_id}/",
    response_model=ConversationResponse,
)
async def update_conv(
    conv_id: uuid.UUID,
    conv_repo: conv_repo_provider,
    conversation: ConversationUpdate,
):

    try:
        return await conv_repo.update(
            conversation.model_dump(exclude_unset=True), id=conv_id
        )
    except IntegrityError:
        raise HTTPException(status_code=404, detail="Conversation not found")


@router.patch(
    "/by_name/{conv_name/",
    response_model=ConversationResponse,
)
async def update_conv(
    conv_name: str,
    conv_repo: conv_repo_provider,
    conversation: ConversationUpdate,
):

    try:
        return await conv_repo.update(
            conversation.model_dump(exclude_unset=True), name=conv_name
        )
    except IntegrityError:
        raise HTTPException(status_code=404, detail="Conversation not found")


@router.post("users/{conv_id}/")
async def add_user_to_conversation(
    conv_id: uuid.UUID,
    conv_repo: conv_repo_provider,
    add_model: AddUser,
) -> None:

    try:
        await conv_repo.add_user(
            user_id=add_model.user_id,
            permission=add_model.is_moder,
            conv_id=conv_id,
        )
    except IntegrityError:
        raise HTTPException(
            status_code=404, detail="User already added or some of id not found"
        )


@router.delete("/{conv_id}/")
async def delete_conv(conv_id: uuid.UUID, conv_repo: conv_repo_provider):
    try:
        return await conv_repo.delete(id=conv_id)
    except IntegrityError:
        raise HTTPException(
            status_code=404, detail="Хз тут все что угодно отъебнуть может"
        )
