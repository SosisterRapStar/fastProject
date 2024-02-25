# from typing import Annotated
#
# from sqlalchemy import select
# from starlette import status
#
# from src.models import db_handler
# from fastapi import Depends, FastAPI, APIRouter, HTTPException
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
#
# from src.models.user_model import User
# from src.schemas.users import UserInDB
#
# router = APIRouter(tags=["Auth"])
#
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
#
# get_token = Annotated[str, Depends(oauth2_scheme)]
#
#
# @router.get("/items/")
# async def read_items(token: get_token):
#     return {"token": token}
#
# def get_user_from_db(username):
#     async with db_handler.session() as ses:
#         stmt = select(User).where(User.name == username)
#         res = ses.scalar(stmt)s
# def get_user(username: str):
#     async with db_handler.session() as ses:
#         stmt = select(User).where(User.name == username)
#         res = ses.scalar(stmt)
#         if res:
#             return UserInDB.model_validate(res, from_attributes=True)
#
#
# def fake_decode_token(token):
#     # This doesn't provide any security at all
#     # Check the next version
#     user = get_user(token)
#     return user
#
#
# async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
#     user = fake_decode_token(token)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid authentication credentials",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     return user
#
#
# async def get_current_active_user(
#         current_user: Annotated[User, Depends(get_current_user)]
# ):
#     if current_user.disabled:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user
#
#
# @router.post("/token")
# async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
#     user_model = get_user
#     user = UserInDB(**user_dict)
#     hashed_password = fake_hash_password(form_data.password)
#     if not hashed_password == user.hashed_password:
#         raise HTTPException(status_code=400, detail="Incorrect username or password")
#
#     return {"access_token": user.username, "token_type": "bearer"}
#
#
# @app.get("/users/me")
# async def read_users_me(
#     current_user: Annotated[User, Depends(get_current_active_user)]
# ):
#     return current_user
