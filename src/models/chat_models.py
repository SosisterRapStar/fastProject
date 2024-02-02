from sqlalchemy import DateTime, ForeignKey, text, String
from sqlalchemy.orm import Mapped
from src.base import Base
from .annotated_types import *


class Convesation(Base):
    __tablename__ = "conversation"

    id: Mapped[UUIDpk]
    status: Mapped[str] = mapped_column(nullable=False)
    is_group: Mapped[bool] = mapped_column(nullable=False, default=False)
    users_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))
    name: Mapped[str | None]
    created_at: Mapped[created_at_timestamp]
    updated_at: Mapped[updated_at_timestamp]

    def __repr__(self) -> str:
        return f"Convesation {self.__dict__}"


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[UUIDpk]
    content: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    created_at: Mapped[created_at_timestamp]
    updated_at: Mapped[updated_at_timestamp]

    def __repr__(self) -> str:
        return f"Message {self.__dict__}"


class User(Base):
    __tablename__ = "user"

    id: Mapped[UUIDpk]
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str] = mapped_column(nullable=False)
    hashed_password: Mapped[str]
    is_online: Mapped[bool] = mapped_column(nullable=False, default=True)
    created_at: Mapped[created_at_timestamp]

    def __repr__(self) -> str:
        return f"User: {self.__dict__}"
