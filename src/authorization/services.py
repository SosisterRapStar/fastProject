from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from src.authorization.security import verify_password
from src.crud.exceptions import RecordNotFoundError
from src.crud.user_repository import UserRepository
from src.models.user_model import User
from src.config import security_settings
from datetime import timedelta
from .security import create_refresh_token, create_access_token
from .token_schema import TokenResponse


async def get_token(data: OAuth2PasswordRequestForm, repo: UserRepository):
    try:
        user = await repo.get(name=data.username)
    except RecordNotFoundError:
        raise HTTPException(
            status_code=400,
            detail="There is nuh uh such user",
            headers={"WWW-Authenticate": "bearer"},
        )


    if not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=400,
            detail="Bro YOO password is wrong",
            headers={"WWW-Authenticate": "bearer"},
        )

    return await _get_user_token(user=user)


async def _get_user_token(user: User, refresh_token=None):
    payload = {"id": str(user.id)}
    access_token_expire = timedelta(minutes=security_settings.ACCES_TOKEN_EXPIRE_MINUTES)

    access_token = await create_access_token(data=payload, expire=access_token_expire)
    if not refresh_token:
        refresh_token = await create_refresh_token(data=payload)

    print(access_token)
    print(refresh_token)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=access_token_expire.seconds,
    )


async def get_refresh_token(user: User):
    pass