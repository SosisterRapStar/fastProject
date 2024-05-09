from fastapi.security import OAuth2PasswordRequestForm
from src.authorization.security import verify_password
from src.crud.exceptions import RecordNotFoundError
from src.crud.user_repository import UserRepository
from src.models.user_model import User
from src.config import settings
from datetime import timedelta

from ..authorization.exceptions import (
    PasswordVerificationError,
    InvalidRefreshTokenError,
    UserCredentialsError,
)
from ..authorization.security import create_token, get_token_payload
from src.schemas.token_schema import TokenResponse
from ..authorization.logger import log


class JWTService:
    __EXPIRE_TIME = timedelta(
        minutes=settings.security_settings.ACCES_TOKEN_EXPIRE_MINUTES
    )
    __REFRESH_EXPIRE_TIME = timedelta(
        minutes=settings.security_settings.REFRESH_TOKEN_EXPIRE_MINUTES
    )

    def __init__(self, repo: UserRepository):
        self.repo = repo
        self.data = None

    def provide_form(self, data: OAuth2PasswordRequestForm):
        self.data = data

    async def get_token(self):
        log.debug("request for token creating")
        data = self.data
        repo = self.repo

        try:
            user = await repo.get(name=data.username)
            verify_password(data.password, user.password)

        except (PasswordVerificationError, RecordNotFoundError):
            raise UserCredentialsError()

        return await self.__get_user_token(user=user)

    async def get_refreshed_token(
        self,
        refresh_token,
    ):
        try:
            payload = get_token_payload(token=refresh_token)
            user_id = payload["id"]
            user = await self.repo.get(id=user_id)

        except (LookupError, RecordNotFoundError):
            raise InvalidRefreshTokenError()

        return await self.__get_user_token(user=user, refresh_token=refresh_token)

    # If refresh token wasn't passed creates two tokens, else refreshes access token

    async def __get_user_token(self, user: User, refresh_token=None):
        payload = {"id": str(user.id)}
        access_token_expire = self.__EXPIRE_TIME
        refresh_token_expire = self.__REFRESH_EXPIRE_TIME
        access_token = await create_token(data=payload, expire=access_token_expire)
        log.debug("access token created")
        if not refresh_token:

            refresh_token = await create_token(
                data=payload, expire=refresh_token_expire
            )
            log.debug("refresh token created")

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=access_token_expire.seconds,
        )
