from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Annotated, Optional

from pydantic import BaseModel, EmailStr, Field, UUID4, ConfigDict
import uuid
from .users import User_on_response


class Message(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    content: str = Field(max_length=100)


class MessageToDb(Message):
    status: str | None
    conversation_fk: uuid.UUID = Field()
    

class MessageFromDb(MessageToDb):
    created_at: datetime
    updated_at: datetime

class MessageFromBroker(Message):
    conversation_id: uuid.UUID

# TODO: here should be the name not UUID
class ResponseMessage(Message):
    model_config = ConfigDict(from_attributes=True)
    author: uuid.UUID = Field(validation_alias="user_fk")
    created_at: datetime
    updated_at: datetime


class ResponseWithUserMessage(ResponseMessage):
    author: Optional[User_on_response] = Field(validation_alias="user")


class UpdateMessage(BaseModel):
    content: str = None
