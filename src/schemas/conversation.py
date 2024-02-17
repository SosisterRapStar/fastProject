from enum import Enum
from typing import TYPE_CHECKING

from pydantic import BaseModel, EmailStr, Field, UUID4, ConfigDict
import uuid
from .users import User_on_response


class ConversationBase(BaseModel):
    name: str = Field(max_length=20)


class ConversationRequest(ConversationBase):
    user_admin_fk: uuid.UUID


class ConversationResponse(ConversationBase):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)
    user_admin_fk: uuid.UUID
