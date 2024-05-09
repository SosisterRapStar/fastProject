import uuid

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .annotated_types import created_at_timestamp, UUIDpk, updated_at_timestamp
from .base import Base
from typing import TYPE_CHECKING, Set
from .friends_model import Friends
from .friends_model import Invite

if TYPE_CHECKING:
    from .chat_models import Conversation, Message, UserConversationSecondary
    


class User(Base):
    __tablename__ = "user"

    name: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        unique=True,
    )
    email: Mapped[str | None] = mapped_column(nullable=False)
    admin_convs: Mapped[list["Conversation"]] = relationship(
        back_populates="user_admin",
        uselist=True,
        cascade="all, delete",
        passive_deletes=True,
    )

    messages: Mapped[list["Message"] | None] = relationship(
        back_populates="user", uselist=True
    )

    sended_invites: Mapped[list["Invite"]] = relationship(
        back_populates="inviter",
        uselist=True,
        cascade="all, delete",
        passive_deletes=True,
        foreign_keys=[Invite.inviter_id],
    )
    received_invites: Mapped[list["Invite"]] = relationship(
        back_populates="invitee",
        uselist=True,
        cascade="all, delete",
        passive_deletes=True,
        foreign_keys=[Invite.invitee_id],
    )

    asoc_conversations: Mapped[list["UserConversationSecondary"]] = relationship(
        back_populates="user",
        uselist=True,
        cascade="all, delete",
        passive_deletes=True,
    )

    friends: Mapped[Set["User"] | None] = relationship(
        "User",
        secondary="friendship",
        primaryjoin="User.id == Friends.user_id",
        secondaryjoin="User.id == Friends.friend_id",
    )

    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    password: Mapped[str | None]  # hashed password

    created_at: Mapped[created_at_timestamp]
    updated_at: Mapped[updated_at_timestamp]

    def __repr__(self):
        return f"User: {self.name}, Id: {self.id}"
