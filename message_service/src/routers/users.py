import uuid
from typing import List, Union
from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError
from starlette import status
from starlette.responses import JSONResponse
import asyncio
from src.authorization.dependency_auth import get_current_user, get_current_user_id
from src.crud.exceptions import RecordNotFoundError
from src.dependencies.dependency_hash import (
    password_hash_dependency,
    update_hash_dependency,
)

from src.dependencies.repo_providers_dependency import user_repo_provider
from src.dependencies.service_dependencies import friends_service_provider
from src.models.friends_model import Invite
from src.models.user_model import User
from src.routers.errors import UserNotFoundError
from src.schemas.conversation import ConversationResponse
from src.schemas.invite_schema import InviteResponse, ReceivedInviteResponse, SendedInviteResponse
from src.schemas.users import User_on_response
# for test
import socket



router = APIRouter(tags=["Users"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def create_user(user: password_hash_dependency, repo: user_repo_provider):

    user = await repo.create(user.model_dump(exclude={"password_repeat"}))

    payload = f"pid: {socket.gethostname()}"
    return JSONResponse(content=payload)


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=User_on_response,
)
async def get_curr_user(user: get_current_user):
    return user



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
    response_model=Union[List[User_on_response], User_on_response],
    status_code=status.HTTP_200_OK,
)
async def get_users(user: get_current_user, user_repo: user_repo_provider, id: uuid.UUID | None = None, name: str | None = None):
    try:
        return await user_repo.get(id=id, name=name)
    except RecordNotFoundError:
        raise UserNotFoundError()
    
    
@router.get(
    "/start/{channel}",
    status_code=status.HTTP_200_OK,
)

@router.patch(
    "/invites/accept/{invite_id}",
    status_code=status.HTTP_200_OK,
)
async def accept_invite(invite_id: uuid.UUID, user: get_current_user, friends_service: friends_service_provider):
    return await friends_service.accept_invite(user=user, invite_id=invite_id)

@router.patch(
    "/invites/declain/{invite_id}",
    status_code=status.HTTP_200_OK,
)
async def declain_invite(invite_id: uuid.UUID, user: get_current_user, friends_service: friends_service_provider):
    return await friends_service.declain_invite(user=user, invite_id=invite_id)

# TODO: handle exceptions
@router.get(
    "/invites/received",
    response_model=List[ReceivedInviteResponse],
    status_code=status.HTTP_200_OK,
)
async def get_all_received_invites(user: get_current_user, friends_service: friends_service_provider):
    return await friends_service.get_received_invites(curr_user=user)

@router.get(
    "/invites/sended",
    response_model=List[SendedInviteResponse],
    status_code=status.HTTP_200_OK,
)
async def get_all_sended_invites(user: get_current_user, friends_service: friends_service_provider):
    return await friends_service.get_sended_invites(curr_user=user)


@router.post(
    "/invites",
    response_model=SendedInviteResponse,
    status_code=status.HTTP_200_OK,
)
async def create_friend_invite(user: get_current_user, friends_service: friends_service_provider, id: uuid.UUID | None = None, name: str | None = None):

    try:
        return await friends_service.create_invite(user=user, id=id, name=name)
    except ValueError:
        raise HTTPException(status_code=400, detail="Query parameters are required")


@router.delete(
    "/invites/{invite_id}",
    status_code=status.HTTP_200_OK,
)
async def create_friend_invite(user: get_current_user, invite_id: uuid.UUID, friends_service: friends_service_provider):

    try:
        return await friends_service.delete_invite(user=user, invite_id=invite_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Query parameters are required")

@router.delete(
    "/friends",
    response_model=User_on_response,
    status_code=status.HTTP_200_OK,
)
async def remove_from_friends(user: get_current_user, friends_service: friends_service_provider, id: uuid.UUID | None = None, name: str | None = None):
    try:
        return await friends_service.remove_from_friends(user=user, id=id, name=name)
    except ValueError:
        raise HTTPException(status_code=400, detail="Query parameters are required")

@router.get(
    "/friends",
    response_model=List[User_on_response],
    status_code=status.HTTP_200_OK,
)
async def get_friends_list(user: get_current_user, friends_service: friends_service_provider):
    return await friends_service.get_all_friends(user=user)
    


@router.get(
    "/convs/",
    response_model=List[ConversationResponse],
)
async def get_user_convs(user: get_current_user, user_repo: user_repo_provider):
    try:
        return await user_repo.get_convs(user_id=user.id)
    except IntegrityError:
        raise UserNotFoundError()


@router.delete("/{user_id}/")
async def delete_user_by_id(
    user_repo: user_repo_provider,
    user_id: uuid.UUID,
):
    try:
        id = await user_repo.delete(id=user_id)
        return JSONResponse(content={'id': str(id)})
    except IntegrityError:
        raise UserNotFoundError()
