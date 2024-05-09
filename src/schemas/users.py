from typing import Annotated, TYPE_CHECKING

from pydantic import BaseModel, EmailStr, Field, UUID4, ConfigDict, model_validator
import uuid

from src.config import settings

if TYPE_CHECKING:
    from .conversation import ConversationResponse


class BaseRequestUser(BaseModel):
    model_config = ConfigDict(extra=settings.schemas_settings.extra)


class BaseUser(BaseModel):
    name: str = Field(
        title="Name of the user",
        max_length=20,
    )
    email: EmailStr


class UserInDB(BaseUser):
    password: str  # hashed


class User_on_request(BaseUser, BaseRequestUser):
    password: str | None = Field(
        max_length=20,
        title="User password",
        default=None,
    )


class User_for_update(BaseUser, BaseRequestUser):
    name: str = Field(title="Nayme of da user", max_length=20, default=None)
    email: EmailStr | None = None
    password: str | None = None


class CreateUser(BaseUser, BaseRequestUser):
    password: str | None = None
    password_repeat: str = None

    # password matching verification can be performed on the frontend
    @model_validator(mode="after")
    def check_passwords_match(self) -> "CreateUser":
        pw1 = self.password
        pw2 = self.password_repeat
        if pw1 is not None and pw2 is not None and pw1 != pw2:
            raise ValueError("Passwords do nah match")
        return self


class User_on_response(BaseUser):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
