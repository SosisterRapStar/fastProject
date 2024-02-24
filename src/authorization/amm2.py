from typing import Annotated

from sqlalchemy import select
from starlette import status

from src.dependencies.repo_providers_dependency import user_repo_provider
from src.models import db_handler
from fastapi import Depends, FastAPI, APIRouter, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from src.models.user_model import User
from src.schemas.users import CreateUser



router = APIRouter(
    tags=["Auth"],
    responses={404: {"detai": "Not found"}},
)

@router.post('/register', status_code=status.HTTP_201_CREATED)
async def create_user(user: CreateUser, repo: user_repo_provider):
    return await repo.create(user.model_dump(exclude={'password_repeat'}))

