from .logger import log
from datetime import timedelta, datetime
from typing import Any

from jose import jwt
from passlib.context import CryptContext

from src.authorization.exceptions import PasswordVerificationError
from src.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    log.debug("password_hashing")
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> None:
    log.debug("password verifying")
    if not pwd_context.verify(plain_password, hashed_password):
        log.exception("An exception occurred: %s", PasswordVerificationError)
        raise PasswordVerificationError


async def create_token(data: dict[str, Any], expire: timedelta):
    payload = time_update_payload(data, expire)
    refresh_token = jwt.encode(
        payload,
        settings.security_settings.JWT_SECRET,
        algorithm=settings.security_settings.JWT_ALGORITHM,
    )
    
    return refresh_token 

def time_update_payload(data, expire: timedelta):
    payload = data.copy()
    expire_in = datetime.utcnow() + expire
    payload.update({"iat": datetime.utcnow(), "exp": expire_in})
    return payload

def get_token_payload(token: str) -> dict:
    payload = jwt.decode(
        token,
        settings.security_settings.JWT_SECRET,
        algorithms=settings.security_settings.JWT_ALGORITHM,
    )

    return payload
