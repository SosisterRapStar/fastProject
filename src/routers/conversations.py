import uuid
from typing import List, Annotated
from fastapi import APIRouter, Path, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.get_dependency import get_by_id_dep
from src.dependencies.hash_dependency import User_on_request_hash_dep
from src.dependencies.session_dependency import session_dep
from src.schemas.conversation import ConversationResponse, ConversationRequest

from src.schemas.users import User_on_response, User_on_request
from src.crud import user_crud, conversation_crud

router = APIRouter(tags=["Conversations"])




@router.post(
    "/{creator_id}/",
    response_model=ConversationResponse,
)
async def demo_create_conversation(creator_id: uuid.UUID, session: session_dep, conversation: ConversationRequest):
    return await conversation_crud.create_conversation(conversation_shema=conversation, async_session=session,
                                                       user_id=creator_id)
@router.post(
    "/{creator_id}",
    response_model=ConversationResponse,
)
async def create_conversation_by_name(creator_id: uuid.UUID, session: session_dep, conversation: ConversationRequest):
    return await conversation_crud.create_conversation(conversation_shema=conversation, async_session=session,
                                                       user_id=creator_id)



@router.get(
    "/",
    tags=["users"],
    response_model=List[User_on_response],
)
async def get_users(session: session_dep):
    return await user_crud.get_users(async_session=session)


@router.get(
    "/{user_id}/",
    tags=["user"],
    response_model=User_on_response,
)
async def get_user_by_id(user: get_by_id_dep):
    return user


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
