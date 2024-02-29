from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Annotated, Optional

from pydantic import BaseModel, EmailStr, Field, UUID4, ConfigDict
import uuid

if TYPE_CHECKING:
    from .users import User_on_response
    from .conversation import ConversationResponse


class Message(BaseModel):
    content: str


class RequestMessage(Message):
    conversation_fk: uuid.UUID


class ResponseMessage(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    created_at: datetime
    updated_at: datetime
    content: str
    author: Optional["User_on_response"] = Field(alies="user")


class UpdateMessage(BaseModel):
    content: str = None
