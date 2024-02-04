import uuid
from typing import List, Annotated
from fastapi import APIRouter, Path, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.dependencies.hash_dependency import User_on_request_hash_dep
from src.models import db_handler
from src.schemas.users import User_on_response, User_on_request
from src.crud import user_crud

router = APIRouter(tags=["Users"])

session_dep = Annotated[AsyncSession, Depends(db_handler.session_dependency)]


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
    "/{user_id}/",
    tags=["user"],
    response_model=User_on_response,
)
async def get_user_by_id(
    user_id: Annotated[uuid.UUID, Path(title="The ID of the item to get")],
    session: session_dep,
):
    user = await user_crud.get_user_by_id(async_session=session, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
