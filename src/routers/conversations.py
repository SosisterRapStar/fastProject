import uuid
from typing import List, Annotated
from fastapi import APIRouter, Path, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.conversation_repository import ConversationRepository
from src.dependencies.hash_dependency import User_on_request_hash_dep
from src.dependencies.session_dependency import session_dep
from src.schemas.conversation import ConversationResponse, ConversationRequest
from src.schemas.user_conversation import ConversationWithUsersResp

from src.schemas.users import User_on_response, User_on_request


router = APIRouter(tags=["Conversations"])


# TODO: убрать явный объект другой природы (сессию) из dependencies в роутах
# сессия должна быть инкапсулирована в работе методов crud и других
# @router.post(
#     "/{creator_id}/",
#     response_model=ConversationResponse,
# )
# async def demo_create_conversation(creator_id: uuid.UUID, session: session_dep, conversation: ConversationRequest):
#     return await conversation_crud.create_conversation(conversation_shema=conversation, async_session=session,
#                                                        user_id=creator_id)


@router.get(
    "/",
    response_model=List[ConversationResponse],
)
async def get_all_conversations(session: session_dep):
    conv_repo = ConversationRepository(session=session)
    return await conv_repo.get()


@router.post(
    "/create/",
    response_model=ConversationResponse,
)
async def create_conversation(session: session_dep, conversation: ConversationRequest):
    conv_repo = ConversationRepository(session=session)
    return await conv_repo.create(conversation.model_dump())


@router.get(
    "/users/{conv_id}/",
    response_model=List[User_on_response],
)
async def get_all_users_in_conv(conv_id: uuid.UUID, session: session_dep):
    conv_repo = ConversationRepository(session=session)
    return await conv_repo.get_users(conv_id=conv_id)


@router.get("/{conv_name}/", response_model=ConversationResponse)
async def get_conv_by_name(conv_name: str, session: session_dep):
    conv_repo = ConversationRepository(session=session)
    return await conv_repo.get(name=conv_name)


@router.get("/by_id/{conv_id}/", response_model=ConversationResponse)
async def get_conv_by_id(conv_id: uuid.UUID, session: session_dep):
    conv_repo = ConversationRepository(session=session)
    return await conv_repo.get(id=conv_id)
