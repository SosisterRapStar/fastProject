from typing import Annotated, TYPE_CHECKING

from pydantic import BaseModel, EmailStr, Field, UUID4, ConfigDict
import uuid

from ..config import schemas_settings

if TYPE_CHECKING:
    from .conversation import ConversationResponse


class BaseRequestUser(BaseModel):
    model_config = ConfigDict(extra=schemas_settings.extra)


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
    name: str = Field(title="Name of the user", max_length=20, default=None)
    email: EmailStr | None = None
    password: str | None = None


class User_on_response(BaseUser):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
