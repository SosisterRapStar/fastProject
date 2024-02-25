# import hashlib
# from typing import Annotated
#
# from fastapi import Depends
#
# from src.schemas.users import User_on_request, User_for_update
#
#
# async def hash_pass(
#     user: User_on_request,
# ) -> User_on_request:
#     user.password = hashlib.sha256(user.password.encode()).hexdigest()
#     return user
#
#
# async def hash_pass_for_update(
#     user: User_for_update,
# ) -> User_for_update:
#     if user.password is not None:
#         user.password = hashlib.sha256(user.password.encode()).hexdigest()
#     return user
#
#
# User_on_request_hash_dep = Annotated[User_on_request, Depends(hash_pass)]
# User_for_update_hash_dep = Annotated[User_for_update, Depends(hash_pass_for_update)]
from datetime import timedelta, datetime

from fastapi import Depends
from starlette.authentication import AuthCredentials, UnauthenticatedUser
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer

from src.config import security_settings
from src.crud.user_repository import UserRepository
from src.dependencies.repo_providers_dependency import user_repo_provider
from src.models import db_handler

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

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


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = get_token_payload(token)
    except JWTError:
        # TODO: actually it means that potentially it is an attack and here should be something serious thing
        return None

    user_id = payload.get('id', None)
    if not user_id:
        return None

    repo = UserRepository(session=next(db_handler.session_dependency()))
    user = repo.get(id=user_id)
    print(user)
    return user



class JWTAuth:
    async def authenticate(self, conn):
        guest = AuthCredentials(['unauthenricated']), UnauthenticatedUser()
        if 'authorization' not in conn.headers:
            return guest

        token = conn.headers.get('authorization').split(' ')[1]  # somnitel'no no OKay
        user = get_current_user(token=token)
        if not user:
            return guest

        return AuthCredentials("authorized"), user



