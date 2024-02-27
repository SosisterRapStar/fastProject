from datetime import timedelta, datetime

from fastapi import Depends
from starlette.authentication import AuthCredentials, UnauthenticatedUser
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer

from src.config import security_settings
from src.crud.user_repository import UserRepository

from src.models import db_handler

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


async def create_access_token(data, expire: timedelta):
    payload = data.copy()
    expire_in = datetime.utcnow() + expire
    payload.update({"iat": datetime.utcnow(), "exp": expire_in})
    token = jwt.encode(
        payload,
        security_settings.JWT_SECRET,
        algorithm=security_settings.JWT_ALGORITHM,
    )
    return token


async def create_refresh_token(data):
    return jwt.encode(
        data,
        security_settings.JWT_SECRET,
        algorithm=security_settings.JWT_ALGORITHM,
    )


def get_token_payload(token):
    payload = jwt.decode(
        token,
        security_settings.JWT_SECRET,
        algorithms=security_settings.JWT_ALGORITHM,
    )

    return payload


# def get_current_user(token: str = Depends(oauth2_scheme)):
#     try:
#         payload = get_token_payload(token)
#     except JWTError:
#         # TODO: actually it means that potentially it is an attack and here should be something serious thing
#         return None
#
#     user_id = payload.get('id', None)
#     if not user_id:
#         return None
#
#     repo = UserRepository(session=next(db_handler.session_dependency()))
#     user = repo.get(id=user_id)
#     print(user)
#     return user
