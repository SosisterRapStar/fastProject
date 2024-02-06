from sqlalchemy import ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, relationship
from .base import Base
from .annotated_types import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user_model import User


class Message(Base):
    __tablename__ = "message"

    content: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(nullable=False)
    user: Mapped["User"] = relationship(
        back_populates="messages",
        uselist=False,
    )
    in_conversation: Mapped["Conversation"] = relationship(back_populates="messages", uselist=False)
    conversation_fk: Mapped[uuid.UUID] = mapped_column(ForeignKey("conversation.id"), unique=True)
    user_fk: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"), unique=True)
    created_at: Mapped[created_at_timestamp]
    updated_at: Mapped[updated_at_timestamp]


class Conversation(Base):
    __tablename__ = "conversation"

    name: Mapped[str | None] = mapped_column(unique=True)
    users: Mapped[list["User"]] = relationship(
        back_populates="conversations",
        uselist=True,
        secondary="user_conversation"
    )
    user_admin: Mapped["User"] = relationship(back_populates="admin_convs", uselist=False)
    user_admin_fk: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"))
    messages: Mapped[list["Message"]] = relationship(back_populates="in_conversation", uselist=True)
    created_at: Mapped[created_at_timestamp]
    updated_at: Mapped[updated_at_timestamp]



UserConversationSecondary = Table("user_conversation",
                                  Base.metadata,
                                  Column("user_fk", ForeignKey("user.id"), primary_key=True),
                                  Column("conversation_fk", ForeignKey("conversation.id"), primary_key=True),
                                  )

