from pydantic import BaseModel, Field, ConfigDict
import uuid

from src.models.friends_model import StatusEnum
from src.models.user_model import User
from src.schemas.users import User_on_response


class InviteToDB(BaseModel):
    inviter_id: uuid.UUID
    invitee_id: uuid.UUID
    status: str = Field(default=StatusEnum.PENDING.value)


class BaseInviteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    status: str = Field(default=StatusEnum.PENDING.value)
    
class SendedInviteResponse(BaseInviteResponse):
    invitee: User_on_response | None
    
class ReceivedInviteResponse(BaseInviteResponse):
    inviter: User_on_response | None

class InviteResponse(BaseInviteResponse):
    inviter: User_on_response
    invitee: User_on_response
   
