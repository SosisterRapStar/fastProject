from pydantic import BaseModel, EmailStr


class BaseUser(BaseModel):
    id: int
    user_name: str
    email: EmailStr


class UserIn(BaseUser):
    password: str


class UserOut(BaseUser):
    pass
