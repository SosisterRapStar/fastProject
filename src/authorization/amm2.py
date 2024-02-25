from typing import Annotated

from jose import JWTError
from sqlalchemy import select
from starlette import status
from starlette.responses import JSONResponse

from src.dependencies.repo_providers_dependency import user_repo_provider
from src.models import db_handler
from fastapi import Depends, FastAPI, APIRouter, HTTPException, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from src.models.user_model import User
from src.schemas.users import CreateUser
from fastapi.security import OAuth2PasswordRequestForm

from .dependency_hash import password_hash_dependency
from .services import get_token, get_refresh_token

router = APIRouter(
    tags=["Auth"],
    responses={404: {"detai": "Not found"}},
)


#
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def create_user(user: password_hash_dependency, repo: user_repo_provider):
    await repo.create(user.model_dump(exclude={"password_repeat"}))
    payload = {"message": "Man YOO have just created a user account"}
    return JSONResponse(content=payload)


@router.post("/token", status_code=status.HTTP_200_OK)
async def authontiticate_user(
    repo: user_repo_provider, data: OAuth2PasswordRequestForm = Depends()
):
    return await get_token(data=data, repo=repo)


@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh_access_token(
    refresh_token: Annotated[str | None, Header()],
    repo: user_repo_provider,
):
    if not refresh_token:
        raise HTTPException(
            status_code=400,
            detail="Token was not passed",
        )
    return await get_refresh_token(token=refresh_token, user_repo=repo)
