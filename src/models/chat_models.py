import uuid

from sqlalchemy import ForeignKey, Table, Column, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, relationship
from src.models.base import Base
from .annotated_types import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user_model import User


class Message(Base):
    __tablename__ = "message"

    content: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(nullable=True)
    user: Mapped["User"] = relationship(
        back_populates="messages",
        uselist=False,
        lazy="joined",
    )
    in_conversation: Mapped["Conversation"] = relationship(
        back_populates="messages", uselist=False
    )
    conversation_fk: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("conversation.id", ondelete="Cascade")
    )
    user_fk: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user.id", ondelete="Cascade")
    )
    created_at: Mapped[created_at_timestamp]
    updated_at: Mapped[updated_at_timestamp]


class Conversation(Base):
    __tablename__ = "conversation"

    name: Mapped[str | None] = mapped_column(unique=True)

    user_admin: Mapped["User"] = relationship(
        back_populates="admin_convs",
        uselist=False,
    )
    user_admin_fk: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE")
    )

    messages: Mapped[list["Message"]] = relationship(
        back_populates="in_conversation",
        uselist=True,
        cascade="all, delete",
        passive_deletes=True,
    )

    asoc_users: Mapped[list["UserConversationSecondary"]] = relationship(
        back_populates="conversation",
        uselist=True,
        cascade="all, delete",
        passive_deletes=True,
    )

    created_at: Mapped[created_at_timestamp]
    updated_at: Mapped[updated_at_timestamp]


class UserConversationSecondary(Base):
    __tablename__ = "user_conversation"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "conversation_id",
            name="unique_pair_keys",
        ),
    )
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    edit_permission: Mapped[bool] = mapped_column(default=False, server_default="False")
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE")
    )
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("conversation.id", ondelete="CASCADE")
    )

    conversation: Mapped["Conversation"] = relationship(back_populates="asoc_users")
    user: Mapped["User"] = relationship(back_populates="asoc_conversations")

    def __repr__(self):
        return f"{self.user_id} | {self.conversation_id}"
