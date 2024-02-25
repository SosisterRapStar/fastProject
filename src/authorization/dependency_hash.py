from typing import Annotated

from fastapi import Depends, HTTPException
from starlette import status

from src.authorization.security import get_password_hash
from src.schemas.users import CreateUser


def hash_and_match_passwords(user: CreateUser) -> CreateUser:
    if user.password != user.password_repeat:
        raise HTTPException(
            status_code=400,
            detail="Passwords do not match",
        )

    user.password = get_password_hash(user.password)
    return user


password_hash_dependency = Annotated[CreateUser, Depends(hash_and_match_passwords)]
