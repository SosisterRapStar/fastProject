from enum import Enum
from typing import TYPE_CHECKING

from pydantic import BaseModel, EmailStr, Field, UUID4, ConfigDict
import uuid

if TYPE_CHECKING:
    from .users import User_on_response


class ConversationBase(BaseModel):
    name: str = Field(max_length=20)


class ConversationRequest(ConversationBase):
    pass


class ConversationResponse(ConversationBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID





