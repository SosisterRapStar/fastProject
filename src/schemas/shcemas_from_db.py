from typing_extensions import Unpack
from src.schemas.message import MessageToDb
from src.schemas.conversation import ConversationBase
import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, model_validator, field_validator
from pydantic import ConfigDict, Field
from src.models.chat_models import Message
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import inspect
    
    
class MessageFromDb(MessageToDb):
    # model_config = ConfigDict(from_attributes=True, extra="forbid")
    created_at: datetime
    updated_at: datetime
    in_coneversation: Optional["ConversationFromDb"] = None
    user_fk: uuid.UUID
    user: Optional["UserFromDb"] = None
    

class ConversationFromDb(ConversationBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    user_admin_fk: uuid.UUID
    created_at: datetime
    updated_at: datetime
    messages: Optional[list[MessageFromDb]]  = None
    


    

class InviteFromDb(BaseModel):
    status: str
    inviter_id: uuid.UUID
    invitee_id: uuid.UUID
    inviter: Optional["UserFromDb"]
    invitee: Optional["UserFromDb"]
    created_at: datetime
    updated_at: datetime
    expire_at: datetime

class UserFromDb(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    id: uuid.UUID
    admin_convs: Optional[List[ConversationFromDb]] 
    messages: Optional[List[MessageFromDb]] 
    sended_invites:  Optional[InviteFromDb] 
    received_invites: Optional[InviteFromDb] 
    friends:  Optional[List["UserFromDb"]] 
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
