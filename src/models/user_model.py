import uuid

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .annotated_types import created_at_timestamp, UUIDpk
from .base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .chat_models import Conversation, Message


class User(Base):
    __tablename__ = "user"

    name: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        unique=True,
    )
    email: Mapped[str | None] = mapped_column(nullable=False)
    admin_convs: Mapped[list["Conversation"]] = relationship(back_populates="user_admin", uselist=True)
    conversations: Mapped[list["Conversation"] | None] = relationship(
        back_populates="users",
        uselist=True,
        secondary="user_conversation",
    )
    messages: Mapped[list["Message"] | None] = relationship(
        back_populates="user", uselist=True, lazy="dynamic"
    )
    password: Mapped[str | None]  # hashed password
    created_at: Mapped[created_at_timestamp]


