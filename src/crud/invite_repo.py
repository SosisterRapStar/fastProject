from src.crud.repo_abstract import CRUDAlchemyRepository
from src.models.friends_model import Invite, StatusEnum
import uuid
from abc import abstractmethod
from repo_abstract import CRUDRepository


class AbstractInviteRepository(CRUDRepository):
    @abstractmethod
    async def accept_invite(self, invite: Invite):
        raise NotImplementedError

    @abstractmethod
    async def accept_invite(self, invite: Invite):
        raise NotImplementedError


class InviteRepository(CRUDAlchemyRepository, AbstractInviteRepository):
    _model = Invite

    async def accept_invite(self, invite: Invite):
        await self.update(
            data={"status": StatusEnum.ACCEPTED.value}, model_object=invite
        )

    async def accept_invite(self, invite: Invite):
        await self.update(
            data={"status": StatusEnum.REJECTED.value}, model_object=invite
        )
