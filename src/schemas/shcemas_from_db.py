from typing_extensions import Unpack
from src.schemas.message import MessageToDb
from src.schemas.conversation import ConversationBase
import uuid
from datetime import datetime
from typing import List, Optional, Union
from pydantic import BaseModel, model_validator, field_validator
from pydantic import ConfigDict, Field
from src.models.chat_models import Message
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import inspect
    
    


class RawDBMessage(MessageToDb):
    created_at: datetime
    updated_at: datetime

class MessageWithConv(RawDBMessage):
    in_coneversation: Optional[Union["RawDBConversation", "ConversationWithMessages"]] = None

class MessageWithUser(RawDBMessage):
    user: Optional["RawDBUser"] = None

class FullMessage(RawDBMessage):
    in_coneversation: Optional["RawDBConversation"] = None
    user: Optional["RawDBUser"] = None


class RawDBConversation(ConversationBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    user_admin_fk: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ConversationWithMessages(RawDBConversation):
    messages: Optional[Union[List[MessageWithUser], List[RawDBMessage], List[MessageWithConv], List[FullMessage]]] = None



class RawDBInvite(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    status: str
    inviter_id: uuid.UUID
    invitee_id: uuid.UUID
    updated_at: datetime
    created_at: datetime
    expire_at: datetime

class InviteWithUsers(BaseModel):
    inviter: Optional["RawDBUser"]
    invitee: Optional["RawDBUser"]

class RawDBUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

class UserWithConvs(RawDBUser):
    admin_convs: List[RawDBConversation] | List[ConversationWithMessages] | None = None

class UserWithMessages(RawDBUser):
    messages: Optional[Union[List[MessageWithUser], List[RawDBMessage], List[MessageWithConv], List[FullMessage]]] = None

class UserWithInvites(RawDBUser):
    sended_invites:  List[RawDBInvite] | List[InviteWithUsers] | None = None
    received_invites: List[RawDBInvite] | List[InviteWithUsers] | None = None

class UserWithFriends(RawDBUser):
    friends:  Optional[List[RawDBUser]] = None

