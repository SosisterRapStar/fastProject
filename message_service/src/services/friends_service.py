from src.crud.exceptions import RecordNotFoundError
from src.crud.invite_repo import AbstractInviteRepository
from src.crud.user_repository import AbstractUserRepository
from src.schemas.invite_schema import InviteToDB
from src.models.user_model import User
from src.models.friends_model import Invite
import uuid
from .logger import log


# TODO: do something here
class FriendException(Exception):
    pass  # DO


class NoAbleToAccept(Exception):
    pass  # DO


# TODO: refactor error handling
class FriendsService:
    def __init__(
        self, invite_repo: AbstractInviteRepository, user_repo: AbstractUserRepository
    ) -> None:
        self.invite_repo = invite_repo
        self.user_repo = user_repo

    async def get_all_friends(self, user: User):
        return await self.user_repo.get_all_friends(user=user)

    async def create_invite(self, user: User, **criteries):
        friend = await self.user_repo.get(**criteries)
        if await self.user_repo.is_in_friend(user=user, friend=friend):
            raise Exception  # for example, will be removed later

        schema = InviteToDB(inviter_id=user.id, invitee_id=friend.id)
        try:
            new_invite = await self.invite_repo.create(schema.model_dump())
            log.debug(f"Created invite {user.id=} to {friend.id=}")

        except Exception:
            log.error(f"Unique constraint error occured {user.id=} and {friend.id=}")
            raise Exception("You have already created invite")  # DO

        await new_invite.awaitable_attrs.invitee
        return new_invite

    async def delete_invite(self, user: User, invite_id: uuid.UUID):
        try:
            log.debug(f"Try to delete invite{invite_id=}")
            invite = await self.invite_repo.get(id=invite_id)
            if invite.inviter_id != user.id:
                raise NoAbleToAccept  # WILL BE changed
            returned_id = await self.invite_repo.delete(model_object=invite)
        except RecordNotFoundError:
            log.error(f"RecordNotFound {invite_id=}")
            raise RecordNotFoundError()  # DO
        log.debug(f"Invite deleted {returned_id=}")
        return returned_id

    async def accept_invite(self, user: User, invite_id: uuid.UUID):

        invite = await self.invite_repo.get(id=invite_id)
        if invite.invitee_id != user.id:
            log.error(f"There is no Invite {invite_id=} for User {user.id=}")
            raise NoAbleToAccept  # DO

        await self.invite_repo.accept_invite(invite=invite)

        log.debug(f"{user.id=} accepted invite {invite_id=}")
        invitee_id = invite.inviter_id

        await self.user_repo.add_friend(user, id=invitee_id)

        log.debug(f"{user.id=} added in friend {invitee_id=}")

        return {"message": "Invite accepted"}

    async def declain_invite(self, user: User, invite_id: uuid.UUID):
        invite = await self.invite_repo.get(id=invite_id)

        if invite.invitee_id != user.id:
            log.error(f"{user.id=} no such invite for user")
            raise NoAbleToAccept

        await self.invite_repo.declain_invite(invite=invite)
        log.debug(f"{user.id=} declained invite {invite.id=}")

        try:
            await self.remove_from_friends(user=user, id=invite.inviter_id)
            log.debug(
                f"Friend {invite.inviter_id=} removed from frineds User {user.id=}"
            )
        except RecordNotFoundError:
            pass

        return {"message": "Invite declained"}

    async def remove_from_friends(self, user: User, **criteries) -> User:
        return await self.user_repo.remove_friend(user=user, **criteries)

    async def get_sended_invites(self, curr_user: User) -> list[Invite]:
        return await self.user_repo.get_sended_invites(user=curr_user)

    async def get_received_invites(self, curr_user: User) -> list[Invite]:
        return await self.user_repo.get_received_invites(user=curr_user)
