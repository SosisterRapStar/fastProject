from src.crud.repo_abstract import CRUDAlchemyRepository
from src.models.friends_model import Invite, StatusEnum
import uuid



class InviteRepository(CRUDAlchemyRepository):
    _model = Invite
    
    async def accept_invite(self, invite: Invite):
        await self.update(data={"status": StatusEnum.ACCEPTED.value}, model_object=invite)
        
        
    async def declain_invite(self, invite: Invite):
        await self.update(data={"status": StatusEnum.REJECTED.value}, model_object=invite)
        
   