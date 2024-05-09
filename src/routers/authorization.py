from typing import Annotated
from starlette import status
from fastapi import Depends, APIRouter, HTTPException, Header
from fastapi.security import OAuth2PasswordRequestForm
from src.authorization.dependency_auth import get_jwt_service


router = APIRouter(
    tags=["Auth"],
    responses={404: {"detai": "Not found"}},
)


@router.post("/token", status_code=status.HTTP_200_OK)
async def authontiticate_user(
    jwt_service: get_jwt_service,
    data: OAuth2PasswordRequestForm = Depends(),
):
    jwt_service.provide_form(data)
    return await jwt_service.get_token()


@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh_access_token(
    refresh_token: Annotated[str | None, Header()],
    jwt_service: get_jwt_service,
):
    if not refresh_token:
        raise HTTPException(
            status_code=400,
            detail="Token was not passed",
        )
    return await jwt_service.get_refreshed_token(refresh_token=refresh_token)
