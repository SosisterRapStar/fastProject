from datetime import timedelta, datetime
from typing import Any

from jose import jwt
from passlib.context import CryptContext

from src.authorization.exceptions import PasswordVerificationError
from src.config import settings
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> None:
    if not pwd_context.verify(plain_password, hashed_password):
        raise PasswordVerificationError


async def create_access_token(data: dict[str, Any], expire: timedelta):
    payload = data.copy()
    expire_in = datetime.utcnow() + expire
    payload.update({"iat": datetime.utcnow(), "exp": expire_in})

    token = jwt.encode(
        payload,
        settings.security_settings.JWT_SECRET,
        algorithm=settings.security_settings.JWT_ALGORITHM,
    )
    return token


async def create_refresh_token(data: dict[str, Any]):
    return jwt.encode(
        data,
        settings.security_settings.JWT_SECRET,
        algorithm=settings.security_settings.JWT_ALGORITHM,
    )


def get_token_payload(token: str) -> dict:
    payload = jwt.decode(
        token,
        settings.security_settings.JWT_SECRET,
        algorithms=settings.security_settings.JWT_ALGORITHM,
    )

    return payload
