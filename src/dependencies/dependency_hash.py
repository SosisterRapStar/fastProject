from typing import Annotated

from fastapi import Depends, HTTPException
from src.authorization.security import get_password_hash
from src.schemas.users import CreateUser, User_for_update


# this is no async cause of CPU bound nature
def hash_and_match_passwords(user: CreateUser) -> CreateUser:
    if user.password != user.password_repeat:
        raise HTTPException(
            status_code=400,
            detail="Passwords do not match",
        )

    user.password = get_password_hash(user.password)
    return user


def hash_pass_for_update(
        user: User_for_update,
) -> User_for_update:
    if user.password is not None:
        user.password = get_password_hash(user.password)
    return user


password_hash_dependency = Annotated[CreateUser, Depends(hash_and_match_passwords)]
update_hash_dependency = Annotated[User_for_update, Depends(hash_pass_for_update)]
