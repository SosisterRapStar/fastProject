from enum import Enum

from pydantic import BaseModel, EmailStr, Field, UUID4, ConfigDict
import uuid


class ConversationBase(BaseModel):
    name: str = Field(max_length=20)


class ConversationRequest(ConversationBase):
    pass


class ConversationResponse(ConversationBase):
    id: uuid.UUID
