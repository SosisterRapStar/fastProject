from pydantic import BaseModel, EmailStr, Field, UUID4, ConfigDict
import uuid


class BaseUser(BaseModel):
    name: str = Field(
        title="Name of the user",
        max_length=20,
    )
    email: EmailStr


class User_on_request(BaseUser):
    password: str | None = Field(
        max_length=20,
        title="User password",
        default=None,
    )


class User_on_response(BaseUser):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID

