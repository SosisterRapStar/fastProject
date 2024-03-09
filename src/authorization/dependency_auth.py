import uuid
from typing import Annotated
from fastapi import Request, Depends, WebSocket
from starlette.datastructures import Headers
from jose import JWTError
from src.authorization.exceptions import NonAuthorizedError, InvalidTokenError
from src.authorization.security import get_token_payload
from src.authorization.services import JWTService
from src.crud.exceptions import RecordNotFoundError
from src.dependencies.repo_providers_dependency import user_repo_provider
from src.models.user_model import User
from .logger import log


async def _get_auth_user_ws(websocket: WebSocket, repo: user_repo_provider) -> User:
    user_id = await _get_auth_user_id(scope=websocket.scope)
    try:
        user = await repo.get(id=user_id)
        log.debug(f"User {user_id} authenticated")

    except RecordNotFoundError:
        log.exception("Non authorized user", RecordNotFoundError)
        raise InvalidTokenError()

    return user


async def _get_auth_user(request: Request, repo: user_repo_provider) -> User:
    user_id = await _get_auth_user_id(scope=request.scope)
    try:
        user = await repo.get(id=user_id)
        log.debug(f"User {user_id} authenticated")

    except RecordNotFoundError:
        log.exception("Non authorized user", RecordNotFoundError)
        raise InvalidTokenError()

    return user


async def _get_auth_user_id(scope) -> uuid.UUID:
    log.debug(f"Request for curr user id")
    user_id = await _id_in_payload(scope=scope)
    return uuid.UUID(user_id)


async def _id_in_payload(scope) -> str:
    headers = Headers(scope=scope)
    try:
        payload = get_token_payload(await _token_in_headers(headers=headers))
        user_id = payload["id"]
    except (LookupError, JWTError):
        log.error("Non authorized user")
        raise NonAuthorizedError()
    return user_id


async def _token_in_headers(headers) -> str:
    try:
        auth_header = headers["Authorization"]
    except LookupError:
        log.error("Non authorized user")
        raise NonAuthorizedError()
    token_type, token = auth_header.split()
    return token


async def _get_JWT_service(repo: user_repo_provider):
    return JWTService(repo=repo)

get_current_user_ws = Annotated[User, Depends(_get_auth_user_ws)]
get_jwt_service = Annotated[JWTService, Depends(_get_JWT_service)]
get_current_user = Annotated[User, Depends(_get_auth_user)]
get_current_user_id = Annotated[User, Depends(_get_auth_user_id)]
