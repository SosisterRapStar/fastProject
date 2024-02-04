from pydantic import BaseModel, EmailStr, Field, UUID4
import uuid


class BaseUser(BaseModel):
    name: str = Field(
        title="Name of the user",
        max_length=20,
    )
    email: EmailStr


class UserIn(BaseUser):
    password: str | None = Field(
        max_length=20,
        title="User password",
    )


class UserOut(BaseUser):
    pass
