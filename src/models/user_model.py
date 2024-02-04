from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .annotated_types import created_at_timestamp
from .base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .chat_models import Convesation, Message


class User(Base):
    __tablename__ = "user"

    name: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        unique=True,
    )
    email: Mapped[str | None] = mapped_column(nullable=False)
    conversations: Mapped[list["Convesation"] | None] = relationship(
        back_populates="users",
        uselist=True,
        secondary="user_conversation",
    )
    messages: Mapped[list["Message"] | None] = relationship(
        back_populates="user", uselist=True
    )
    hashed_password: Mapped[str | None]
    created_at: Mapped[created_at_timestamp]
