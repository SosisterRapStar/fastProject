from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship
from .base import Base
from .annotated_types import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user_model import User


class Message(Base):
    __tablename__ = "messages"

    content: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(nullable=False)
    user: Mapped["User"] = relationship(
        back_populates="messages",
        uselist=False,
    )
    user_fk: Mapped[UUIDpk] = mapped_column(ForeignKey("user.id"))
    created_at: Mapped[created_at_timestamp]
    updated_at: Mapped[updated_at_timestamp]


class Convesation(Base):
    __tablename__ = "conversation"

    status: Mapped[str] = mapped_column(nullable=False)
    is_group: Mapped[bool] = mapped_column(nullable=False)
    name: Mapped[str | None]
    users: Mapped[list["User"]] = relationship(
        back_populates="conversations",
        uselist=True,
        secondary="user_conversation",
    )
    created_at: Mapped[created_at_timestamp]
    updated_at: Mapped[updated_at_timestamp]


class UserConversationSecondary(Base):
    __tablename__ = "user_conversation"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_fk = mapped_column(ForeignKey("user.id"))
    conversation_fk = mapped_column(ForeignKey("conversation.id"))
