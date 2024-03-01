from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Annotated, Optional

from pydantic import BaseModel, EmailStr, Field, UUID4, ConfigDict
import uuid
from .users import User_on_response


class Message(BaseModel):
    content: str


class RequestMessage(Message):
    conversation_fk: str = Field()


class ResponseMessage(Message):
    model_config = ConfigDict(from_attributes=True)
    author: uuid.UUID = Field(validation_alias="user_fk")
    created_at: datetime
    updated_at: datetime


class ResponseWithUserMessage(ResponseMessage):
    author: Optional[User_on_response] = Field(validation_alias="user")


class UpdateMessage(BaseModel):
    content: str = None
