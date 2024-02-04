import hashlib
from typing import Annotated

from fastapi import Depends

from src.schemas.users import User_on_request

hashlib.sha256()


def hash_pass(user: User_on_request) -> User_on_request:
    user.password = hashlib.sha256(user.password.encode()).hexdigest()
    return user


User_on_request_hash_dep = Annotated[User_on_request, Depends(hash_pass)]
