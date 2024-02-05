from enum import Enum

from pydantic import BaseModel, EmailStr, Field, UUID4, ConfigDict
import uuid


class BaseConversation(BaseModel):
    status: str = "Personal"
    name: str = Field(max_length=20, default="Personal")


class GroupConversation(BaseConversation):
    status: str = "Group"
    name: str = ""

class User_for_update(BaseUser):
    name: str = Field(
        title="Name of the user",
        max_length=20,
        default=None
    )
    email: EmailStr | None = None
    password: str | None = None


class User_on_response(BaseUser):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
