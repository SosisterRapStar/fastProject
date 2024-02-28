import uuid
from typing import Annotated
from fastapi import Request, Depends
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError
from src.authorization.exceptions import NonAuthorizedError, InvalidTokenError
from src.authorization.security import get_token_payload
from src.authorization.services import JWTService
from src.crud.exceptions import RecordNotFoundError
from src.dependencies.repo_providers_dependency import user_repo_provider
from src.models.user_model import User



async def _get_auth_user_id(request: Request) -> uuid.UUID:
    try:
        auth_header = request.headers["Authorization"]
    except LookupError:
        raise NonAuthorizedError()
    token_type, token = auth_header.split()
    try:
        payload = get_token_payload(token)
        user_id = payload["id"]
    except (LookupError, JWTError):
        raise NonAuthorizedError()

    return user_id


async def _get_auth_user(request: Request, repo: user_repo_provider) -> User:
    user_id = await _get_auth_user_id(request)

    try:
        user = await repo.get(id=user_id)
    except RecordNotFoundError:
        raise InvalidTokenError()

    return user



async def _get_JWT_service(
        repo: user_repo_provider
):
    return JWTService(repo=repo)


get_jwt_service = Annotated[JWTService, Depends(_get_JWT_service)]
get_current_user = Annotated[User, Depends(_get_auth_user)]
get_current_user_id = Annotated[User, Depends(_get_auth_user_id)]
