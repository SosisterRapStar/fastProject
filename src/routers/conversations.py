import uuid
from typing import List, Annotated
from fastapi import APIRouter, Path, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.conversation_crud import create_conversation_and_add_admin, get_conv_with_users, get_conv_by_name
from src.dependencies.get_dependency import get_by_id_dep
from src.dependencies.hash_dependency import User_on_request_hash_dep
from src.dependencies.session_dependency import session_dep
from src.schemas.conversation import ConversationResponse, ConversationRequest
from src.schemas.user_conversation import ConversationWithUsersResp

from src.schemas.users import User_on_response, User_on_request
from src.crud import user_crud, conversation_crud

router = APIRouter(tags=["Conversations"])




# @router.post(
#     "/{creator_id}/",
#     response_model=ConversationResponse,
# )
# async def demo_create_conversation(creator_id: uuid.UUID, session: session_dep, conversation: ConversationRequest):
#     return await conversation_crud.create_conversation(conversation_shema=conversation, async_session=session,
#                                                        user_id=creator_id)


@router.post(
    "create/{creator_id}/",
    response_model=ConversationResponse,
)
async def demo_create_conversation(creator_id: uuid.UUID, session: session_dep, conversation: ConversationRequest):
    return await create_conversation_and_add_admin(async_session=session,
                                                   user_id=creator_id,
                                                   conversation_schema=conversation,)



@router.get(
    "all/{conv_name}/",
    response_model=ConversationWithUsersResp,
)
async def demo_get_all_users_in_conv(conv_name: str, session: session_dep):
    return await get_conv_with_users(async_session=session, conv_name=conv_name)


@router.get("/{conv_name}/",
            response_model=ConversationResponse)
async def demo_get_conv_by_name(conv_name: str, session: session_dep):
    return await get_conv_by_name(async_session=session, conv_name=conv_name)
