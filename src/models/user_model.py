import uuid

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .annotated_types import created_at_timestamp, UUIDpk, updated_at_timestamp
from .base import Base
from typing import TYPE_CHECKING

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
        back_populates="user_admin", uselist=True, cascade="all, delete",
        passive_deletes=True,
    )

    messages: Mapped[list["Message"] | None] = relationship(
        back_populates="user", uselist=True
    )

    asoc_conversations: Mapped[list["UserConversationSecondary"]] = relationship(
        back_populates="user",
        uselist=True,
        cascade="all, delete",
        passive_deletes=True,

    )

    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)


    password: Mapped[str | None]  # hashed password

    created_at: Mapped[created_at_timestamp]
    updated_at: Mapped[updated_at_timestamp]

