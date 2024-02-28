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
