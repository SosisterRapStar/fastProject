from typing import Annotated

from fastapi import Request, HTTPException, Depends
from jose import JWTError

from src.authorization.security import get_token_payload
from src.crud.exceptions import RecordNotFoundError
from src.dependencies.repo_providers_dependency import user_repo_provider
from src.models.user_model import User


async def _get_user_from_JWT(request: Request, repo: user_repo_provider) -> User:
    auth_header = request.headers.get("Authorization", None)
    if not auth_header:
        raise HTTPException(
            status_code=401,
            detail="Non authorized user",
        )

    token_type, token = auth_header.split()

    if token_type != "Bearer":
        raise HTTPException(
            status_code=401,
            detail="Invalid token type",
        )
    try:
        payload = get_token_payload(token)
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("id", None)
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user = await repo.get(id=user_id)
    except RecordNotFoundError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


get_current_user = Annotated[User, Depends(_get_user_from_JWT)]
